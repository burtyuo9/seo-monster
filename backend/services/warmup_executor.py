"""
Warmup Executor - Сервис автоматического выполнения прогрева AWS SES
Интегрирует warmup планы с системой рассылок
"""

import json
import os
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import time

# AWS SDK
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

from services.ses_warmup import warmup_manager, WarmupStatus
from services.aws_ses_service import ses_service
from services.recipient_manager import recipient_manager
from services.email_content_generator import email_generator

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)


class WarmupExecutor:
    """Исполнитель автоматического прогрева"""
    
    def __init__(self):
        self.execution_log: List[Dict] = []
        self.is_running = False
        self._scheduler_thread = None
        self._check_interval = 60  # Check every minute
        self._load_log()
    
    def _load_log(self):
        """Загрузка лога выполнения"""
        try:
            log_file = os.path.join(DATA_DIR, 'warmup_execution_log.json')
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    self.execution_log = json.load(f)
        except Exception as e:
            print(f"Error loading warmup log: {e}")
    
    def _save_log(self):
        """Сохранение лога выполнения"""
        try:
            log_file = os.path.join(DATA_DIR, 'warmup_execution_log.json')
            # Keep only last 1000 entries
            self.execution_log = self.execution_log[-1000:]
            with open(log_file, 'w') as f:
                json.dump(self.execution_log, f, indent=2)
        except Exception as e:
            print(f"Error saving warmup log: {e}")
    
    def _log_execution(self, plan_id: str, action: str, status: str, 
                       details: Dict = None, error: str = None):
        """Добавление записи в лог"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "plan_id": plan_id,
            "action": action,
            "status": status,
            "details": details or {},
            "error": error
        }
        self.execution_log.append(entry)
        self._save_log()
    
    async def execute_warmup_for_plan(self, plan_id: str) -> Dict:
        """
        Выполнение прогрева для конкретного плана
        Отправляет emails согласно расписанию прогрева
        """
        plan = warmup_manager.get_plan(plan_id)
        if not plan:
            return {"success": False, "error": "Plan not found"}
        
        if plan.status != WarmupStatus.IN_PROGRESS:
            return {"success": False, "error": f"Plan is not in progress (status: {plan.status.value})"}
        
        # Проверяем конфигурацию
        if not plan.recipient_list_id:
            self._log_execution(plan_id, "execute", "failed", error="No recipient list configured")
            return {"success": False, "error": "No recipient list configured"}
        
        if not plan.content_id:
            self._log_execution(plan_id, "execute", "failed", error="No email content configured")
            return {"success": False, "error": "No email content configured"}
        
        if not plan.from_email:
            self._log_execution(plan_id, "execute", "failed", error="No sender email configured")
            return {"success": False, "error": "No sender email configured"}
        
        # Получаем AWS ключ
        key_info = ses_service.get_key_info(plan.key_id)
        if not key_info:
            self._log_execution(plan_id, "execute", "failed", error="AWS key not found")
            return {"success": False, "error": "AWS key not found"}
        
        # Получаем полные данные ключа (с секретом)
        full_key = ses_service.keys.get(plan.key_id)
        if not full_key:
            return {"success": False, "error": "AWS key data not found"}
        
        # Получаем список получателей
        recipient_list = recipient_manager.get_list(plan.recipient_list_id)
        if not recipient_list:
            self._log_execution(plan_id, "execute", "failed", error="Recipient list not found")
            return {"success": False, "error": "Recipient list not found"}
        
        # Получаем контент письма
        content = email_generator.get_content(plan.content_id)
        if not content:
            self._log_execution(plan_id, "execute", "failed", error="Email content not found")
            return {"success": False, "error": "Email content not found"}
        
        # Определяем объем отправки на сегодня
        target_volume = warmup_manager.get_today_volume(plan_id)
        
        # Проверяем квоту AWS
        remaining_quota = key_info.get('remaining_quota', 0)
        if target_volume > remaining_quota:
            self._log_execution(plan_id, "execute", "warning", 
                              details={"target": target_volume, "available": remaining_quota},
                              error="Insufficient quota, reducing volume")
            target_volume = remaining_quota
        
        if target_volume <= 0:
            self._log_execution(plan_id, "execute", "skipped", 
                              details={"reason": "No quota available"})
            return {"success": False, "error": "No quota available"}
        
        # Получаем получателей для отправки
        recipients_result = recipient_manager.get_recipients(
            plan.recipient_list_id, 
            limit=target_volume,
            offset=plan.total_sent % recipient_list.get('valid_count', target_volume)
        )
        
        if not recipients_result.get('success'):
            return {"success": False, "error": "Failed to get recipients"}
        
        recipients = recipients_result.get('recipients', [])
        
        if not recipients:
            self._log_execution(plan_id, "execute", "failed", error="No recipients available")
            return {"success": False, "error": "No recipients available"}
        
        # Выполняем отправку
        result = await self._send_warmup_emails(
            plan=plan,
            key_data=full_key,
            content=content,
            recipients=recipients,
            target_volume=min(target_volume, len(recipients))
        )
        
        return result
    
    async def _send_warmup_emails(self, plan, key_data: Dict, content: Dict, 
                                   recipients: List[Dict], target_volume: int) -> Dict:
        """Отправка warmup писем"""
        
        if not AWS_AVAILABLE:
            # Симуляция для тестирования
            return await self._simulate_sending(plan, target_volume)
        
        try:
            ses_client = boto3.client(
                'ses',
                aws_access_key_id=key_data['access_key_id'],
                aws_secret_access_key=key_data['secret_access_key'],
                region_name=key_data['region']
            )
            
            sent = 0
            delivered = 0
            bounced = 0
            complaints = 0
            errors = []
            
            # Определяем задержку между письмами для соблюдения rate limit
            max_rate = key_data.get('max_send_rate', 1)
            delay = 1.0 / max_rate if max_rate > 0 else 1.0
            
            # Подготавливаем контент
            subject = content.get('subject', 'Warmup Email')
            html_body = content.get('html_body', '')
            text_body = content.get('text_body', '')
            
            from_address = f"{plan.from_name} <{plan.from_email}>" if plan.from_name else plan.from_email
            
            for i, recipient in enumerate(recipients[:target_volume]):
                try:
                    email = recipient.get('email', '').strip()
                    if not email:
                        continue
                    
                    # Персонализация (если есть переменные)
                    personalized_subject = subject
                    personalized_html = html_body
                    personalized_text = text_body
                    
                    # Простая персонализация
                    for key, value in recipient.items():
                        placeholder = f"{{{{{key}}}}}"
                        personalized_subject = personalized_subject.replace(placeholder, str(value))
                        personalized_html = personalized_html.replace(placeholder, str(value))
                        personalized_text = personalized_text.replace(placeholder, str(value))
                    
                    # Формируем тело письма
                    body = {}
                    if html_body:
                        body['Html'] = {'Charset': 'UTF-8', 'Data': personalized_html}
                    if text_body:
                        body['Text'] = {'Charset': 'UTF-8', 'Data': personalized_text}
                    
                    if not body:
                        body['Text'] = {'Charset': 'UTF-8', 'Data': 'Warmup email'}
                    
                    # Отправляем
                    response = ses_client.send_email(
                        Source=from_address,
                        Destination={'ToAddresses': [email]},
                        Message={
                            'Subject': {'Charset': 'UTF-8', 'Data': personalized_subject},
                            'Body': body
                        }
                    )
                    
                    sent += 1
                    delivered += 1  # Предполагаем доставку, реальные данные придут через SNS
                    
                    # Задержка между письмами
                    if delay > 0 and i < target_volume - 1:
                        await asyncio.sleep(delay)
                    
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code in ['MessageRejected', 'MailFromDomainNotVerified']:
                        bounced += 1
                    errors.append(f"{email}: {error_code}")
                except Exception as e:
                    errors.append(f"{email}: {str(e)}")
            
            # Записываем статистику дня
            warmup_manager.record_day_stats(
                plan_id=plan.id,
                day=plan.current_day,
                sent=sent,
                delivered=delivered,
                bounced=bounced,
                complaints=complaints,
                opens=0,
                clicks=0
            )
            
            self._log_execution(plan.id, "execute", "success", details={
                "day": plan.current_day,
                "target": target_volume,
                "sent": sent,
                "delivered": delivered,
                "bounced": bounced,
                "errors_count": len(errors)
            })
            
            return {
                "success": True,
                "plan_id": plan.id,
                "day": plan.current_day,
                "target_volume": target_volume,
                "sent": sent,
                "delivered": delivered,
                "bounced": bounced,
                "errors": errors[:10]  # First 10 errors
            }
            
        except Exception as e:
            self._log_execution(plan.id, "execute", "failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _simulate_sending(self, plan, target_volume: int) -> Dict:
        """Симуляция отправки для тестирования (когда AWS недоступен)"""
        
        # Симулируем реалистичные метрики
        sent = target_volume
        delivery_rate = random.uniform(0.95, 0.99)
        delivered = int(sent * delivery_rate)
        bounced = sent - delivered
        complaint_rate = random.uniform(0.0001, 0.001)
        complaints = int(sent * complaint_rate)
        open_rate = random.uniform(0.15, 0.35)
        opens = int(delivered * open_rate)
        click_rate = random.uniform(0.02, 0.08)
        clicks = int(opens * click_rate)
        
        # Записываем статистику
        warmup_manager.record_day_stats(
            plan_id=plan.id,
            day=plan.current_day,
            sent=sent,
            delivered=delivered,
            bounced=bounced,
            complaints=complaints,
            opens=opens,
            clicks=clicks
        )
        
        self._log_execution(plan.id, "simulate", "success", details={
            "day": plan.current_day,
            "sent": sent,
            "delivered": delivered,
            "bounced": bounced,
            "opens": opens,
            "clicks": clicks,
            "mode": "simulation"
        })
        
        return {
            "success": True,
            "plan_id": plan.id,
            "day": plan.current_day,
            "target_volume": target_volume,
            "sent": sent,
            "delivered": delivered,
            "bounced": bounced,
            "complaints": complaints,
            "opens": opens,
            "clicks": clicks,
            "mode": "simulation"
        }
    
    def start_scheduler(self):
        """Запуск планировщика автоматического прогрева"""
        if self.is_running:
            return {"success": False, "message": "Scheduler already running"}
        
        self.is_running = True
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        
        self._log_execution("system", "scheduler_start", "success")
        return {"success": True, "message": "Scheduler started"}
    
    def stop_scheduler(self):
        """Остановка планировщика"""
        self.is_running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        
        self._log_execution("system", "scheduler_stop", "success")
        return {"success": True, "message": "Scheduler stopped"}
    
    def _scheduler_loop(self):
        """Основной цикл планировщика"""
        while self.is_running:
            try:
                self._check_and_execute_due_plans()
            except Exception as e:
                self._log_execution("system", "scheduler_error", "error", error=str(e))
            
            time.sleep(self._check_interval)
    
    def _check_and_execute_due_plans(self):
        """Проверка и выполнение планов, которые должны быть выполнены"""
        now = datetime.now()
        
        for plan in warmup_manager.get_active_plans():
            if not plan.auto_mode:
                continue
            
            # Проверяем, пора ли отправлять
            if plan.send_hour == now.hour and plan.send_minute <= now.minute:
                # Проверяем, не отправляли ли уже сегодня
                if plan.last_auto_run:
                    last_run = datetime.fromisoformat(plan.last_auto_run)
                    if last_run.date() == now.date():
                        continue
                
                # Выполняем отправку в отдельном потоке
                asyncio.run(self.execute_warmup_for_plan(plan.id))
    
    def get_execution_log(self, plan_id: str = None, limit: int = 100) -> List[Dict]:
        """Получение лога выполнения"""
        if plan_id:
            filtered = [e for e in self.execution_log if e.get('plan_id') == plan_id]
        else:
            filtered = self.execution_log
        
        return filtered[-limit:]
    
    def get_scheduler_status(self) -> Dict:
        """Получение статуса планировщика"""
        active_plans = warmup_manager.get_active_plans()
        auto_plans = [p for p in active_plans if p.auto_mode]
        
        return {
            "is_running": self.is_running,
            "active_plans": len(active_plans),
            "auto_mode_plans": len(auto_plans),
            "check_interval_seconds": self._check_interval,
            "total_log_entries": len(self.execution_log),
            "last_check": datetime.now().isoformat() if self.is_running else None
        }


# Глобальный экземпляр
warmup_executor = WarmupExecutor()
