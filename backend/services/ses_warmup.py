"""
SES Warm-up Manager - Automatic warmup for new AWS SES keys
Extended version with automatic scheduler, email integration, and monitoring
"""

import json
import os
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
import time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

class WarmupStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class WarmupStrategy(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

@dataclass
class WarmupDay:
    day: int
    target_volume: int
    actual_sent: int = 0
    delivered: int = 0
    bounced: int = 0
    complaints: int = 0
    opens: int = 0
    clicks: int = 0
    date: str = ""
    completed: bool = False
    send_time: str = ""  # Time when emails were sent
    
    @property
    def delivery_rate(self) -> float:
        return (self.delivered / self.actual_sent * 100) if self.actual_sent > 0 else 0.0
    
    @property
    def bounce_rate(self) -> float:
        return (self.bounced / self.actual_sent * 100) if self.actual_sent > 0 else 0.0
    
    @property
    def complaint_rate(self) -> float:
        return (self.complaints / self.actual_sent * 100) if self.actual_sent > 0 else 0.0
    
    @property
    def open_rate(self) -> float:
        return (self.opens / self.delivered * 100) if self.delivered > 0 else 0.0
    
    @property
    def click_rate(self) -> float:
        return (self.clicks / self.delivered * 100) if self.delivered > 0 else 0.0

@dataclass
class WarmupPlan:
    id: str
    key_id: str
    name: str
    strategy: WarmupStrategy
    status: WarmupStatus
    start_date: str
    target_daily_volume: int
    current_day: int = 1
    total_days: int = 14
    schedule: List[WarmupDay] = field(default_factory=list)
    max_bounce_rate: float = 5.0
    max_complaint_rate: float = 0.1
    auto_pause_on_issues: bool = True
    total_sent: int = 0
    total_delivered: int = 0
    total_bounced: int = 0
    total_complaints: int = 0
    total_opens: int = 0
    total_clicks: int = 0
    created_at: str = ""
    updated_at: str = ""
    
    # New fields for automation
    auto_mode: bool = True
    send_hour: int = 10  # Hour of day to send (0-23)
    send_minute: int = 0
    recipient_list_id: str = ""  # List to send warmup emails to
    content_id: str = ""  # Email content to use
    from_email: str = ""  # Verified sender email
    from_name: str = ""
    last_auto_run: str = ""
    next_scheduled_run: str = ""
    pause_reason: str = ""
    
    # Monitoring
    health_score: float = 100.0  # 0-100 score based on metrics
    reputation_trend: str = "stable"  # improving, stable, declining
    alerts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id, 'key_id': self.key_id, 'name': self.name,
            'strategy': self.strategy.value, 'status': self.status.value,
            'start_date': self.start_date, 'target_daily_volume': self.target_daily_volume,
            'current_day': self.current_day, 'total_days': self.total_days,
            'schedule': [asdict(day) for day in self.schedule],
            'max_bounce_rate': self.max_bounce_rate, 'max_complaint_rate': self.max_complaint_rate,
            'auto_pause_on_issues': self.auto_pause_on_issues,
            'total_sent': self.total_sent, 'total_delivered': self.total_delivered,
            'total_bounced': self.total_bounced, 'total_complaints': self.total_complaints,
            'total_opens': self.total_opens, 'total_clicks': self.total_clicks,
            'created_at': self.created_at, 'updated_at': self.updated_at,
            'auto_mode': self.auto_mode, 'send_hour': self.send_hour, 'send_minute': self.send_minute,
            'recipient_list_id': self.recipient_list_id, 'content_id': self.content_id,
            'from_email': self.from_email, 'from_name': self.from_name,
            'last_auto_run': self.last_auto_run, 'next_scheduled_run': self.next_scheduled_run,
            'pause_reason': self.pause_reason, 'health_score': self.health_score,
            'reputation_trend': self.reputation_trend, 'alerts': self.alerts,
            'progress_percent': round((self.current_day - 1) / self.total_days * 100, 1) if self.total_days > 0 else 0,
            'avg_delivery_rate': self._calc_avg_delivery_rate(),
            'avg_bounce_rate': self._calc_avg_bounce_rate(),
            'avg_complaint_rate': self._calc_avg_complaint_rate(),
            'avg_open_rate': self._calc_avg_open_rate()
        }
    
    def _calc_avg_delivery_rate(self) -> float:
        completed = [d for d in self.schedule if d.completed and d.actual_sent > 0]
        if not completed:
            return 0.0
        return round(sum(d.delivery_rate for d in completed) / len(completed), 2)
    
    def _calc_avg_bounce_rate(self) -> float:
        completed = [d for d in self.schedule if d.completed and d.actual_sent > 0]
        if not completed:
            return 0.0
        return round(sum(d.bounce_rate for d in completed) / len(completed), 2)
    
    def _calc_avg_complaint_rate(self) -> float:
        completed = [d for d in self.schedule if d.completed and d.actual_sent > 0]
        if not completed:
            return 0.0
        return round(sum(d.complaint_rate for d in completed) / len(completed), 3)
    
    def _calc_avg_open_rate(self) -> float:
        completed = [d for d in self.schedule if d.completed and d.delivered > 0]
        if not completed:
            return 0.0
        return round(sum(d.open_rate for d in completed) / len(completed), 2)

WARMUP_TEMPLATES = {
    WarmupStrategy.CONSERVATIVE: {
        'days': 21, 
        'volumes': [50, 100, 150, 200, 300, 400, 500, 700, 900, 1200, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 7500, 9000, 10000, 12000],
        'description': 'Медленный и безопасный прогрев за 21 день. Лучший выбор для новых доменов.'
    },
    WarmupStrategy.MODERATE: {
        'days': 14, 
        'volumes': [100, 200, 400, 600, 1000, 1500, 2000, 3000, 4000, 5500, 7000, 9000, 11000, 14000],
        'description': 'Сбалансированный прогрев за 14 дней. Подходит для большинства случаев.'
    },
    WarmupStrategy.AGGRESSIVE: {
        'days': 7, 
        'volumes': [500, 1000, 2500, 5000, 8000, 12000, 20000],
        'description': 'Быстрый прогрев за 7 дней. Повышенный риск проблем с доставляемостью.'
    }
}

class SESWarmupManager:
    def __init__(self):
        self.plans: Dict[str, WarmupPlan] = {}
        self._scheduler_running = False
        self._scheduler_thread = None
        self._send_callback: Optional[Callable] = None
        self._load_data()
    
    def _load_data(self):
        try:
            filepath = os.path.join(DATA_DIR, 'warmup_plans.json')
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    for plan_data in data.get('plans', []):
                        schedule = [WarmupDay(**d) for d in plan_data.get('schedule', [])]
                        plan = WarmupPlan(
                            id=plan_data['id'], key_id=plan_data['key_id'], name=plan_data['name'],
                            strategy=WarmupStrategy(plan_data['strategy']),
                            status=WarmupStatus(plan_data['status']),
                            start_date=plan_data['start_date'],
                            target_daily_volume=plan_data['target_daily_volume'],
                            current_day=plan_data.get('current_day', 1),
                            total_days=plan_data.get('total_days', 14),
                            schedule=schedule,
                            max_bounce_rate=plan_data.get('max_bounce_rate', 5.0),
                            max_complaint_rate=plan_data.get('max_complaint_rate', 0.1),
                            auto_pause_on_issues=plan_data.get('auto_pause_on_issues', True),
                            total_sent=plan_data.get('total_sent', 0),
                            total_delivered=plan_data.get('total_delivered', 0),
                            total_bounced=plan_data.get('total_bounced', 0),
                            total_complaints=plan_data.get('total_complaints', 0),
                            total_opens=plan_data.get('total_opens', 0),
                            total_clicks=plan_data.get('total_clicks', 0),
                            created_at=plan_data.get('created_at', ''),
                            updated_at=plan_data.get('updated_at', ''),
                            auto_mode=plan_data.get('auto_mode', True),
                            send_hour=plan_data.get('send_hour', 10),
                            send_minute=plan_data.get('send_minute', 0),
                            recipient_list_id=plan_data.get('recipient_list_id', ''),
                            content_id=plan_data.get('content_id', ''),
                            from_email=plan_data.get('from_email', ''),
                            from_name=plan_data.get('from_name', ''),
                            last_auto_run=plan_data.get('last_auto_run', ''),
                            next_scheduled_run=plan_data.get('next_scheduled_run', ''),
                            pause_reason=plan_data.get('pause_reason', ''),
                            health_score=plan_data.get('health_score', 100.0),
                            reputation_trend=plan_data.get('reputation_trend', 'stable'),
                            alerts=plan_data.get('alerts', [])
                        )
                        self.plans[plan.id] = plan
        except Exception as e:
            print(f"Error loading warmup data: {e}")
    
    def _save_data(self):
        try:
            filepath = os.path.join(DATA_DIR, 'warmup_plans.json')
            data = {'plans': [plan.to_dict() for plan in self.plans.values()]}
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving warmup data: {e}")
    
    def create_plan(self, key_id: str, name: str, strategy: str, target_volume: int,
                    auto_mode: bool = True, send_hour: int = 10, send_minute: int = 0,
                    recipient_list_id: str = "", content_id: str = "",
                    from_email: str = "", from_name: str = "") -> WarmupPlan:
        """Create a new warmup plan with optional automation settings"""
        plan_id = f"warmup_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        strat = WarmupStrategy(strategy)
        template = WARMUP_TEMPLATES[strat]
        
        schedule = []
        scale_factor = target_volume / template['volumes'][-1]
        
        for i, vol in enumerate(template['volumes']):
            scaled_vol = max(int(vol * scale_factor), vol)
            schedule.append(WarmupDay(day=i+1, target_volume=scaled_vol))
        
        plan = WarmupPlan(
            id=plan_id, key_id=key_id, name=name, strategy=strat,
            status=WarmupStatus.NOT_STARTED, start_date="",
            target_daily_volume=target_volume, total_days=template['days'],
            schedule=schedule, created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            auto_mode=auto_mode, send_hour=send_hour, send_minute=send_minute,
            recipient_list_id=recipient_list_id, content_id=content_id,
            from_email=from_email, from_name=from_name
        )
        self.plans[plan_id] = plan
        self._save_data()
        return plan
    
    def update_plan_settings(self, plan_id: str, **kwargs) -> Optional[WarmupPlan]:
        """Update plan settings"""
        plan = self.plans.get(plan_id)
        if not plan:
            return None
        
        allowed_fields = ['auto_mode', 'send_hour', 'send_minute', 'recipient_list_id',
                         'content_id', 'from_email', 'from_name', 'max_bounce_rate',
                         'max_complaint_rate', 'auto_pause_on_issues', 'name']
        
        for key, value in kwargs.items():
            if key in allowed_fields and hasattr(plan, key):
                setattr(plan, key, value)
        
        plan.updated_at = datetime.now().isoformat()
        self._update_next_scheduled_run(plan)
        self._save_data()
        return plan
    
    def _update_next_scheduled_run(self, plan: WarmupPlan):
        """Calculate next scheduled run time"""
        if plan.status != WarmupStatus.IN_PROGRESS or not plan.auto_mode:
            plan.next_scheduled_run = ""
            return
        
        now = datetime.now()
        next_run = now.replace(hour=plan.send_hour, minute=plan.send_minute, second=0, microsecond=0)
        
        if next_run <= now:
            next_run += timedelta(days=1)
        
        plan.next_scheduled_run = next_run.isoformat()
    
    def start_plan(self, plan_id: str) -> Optional[WarmupPlan]:
        plan = self.plans.get(plan_id)
        if plan and plan.status in [WarmupStatus.NOT_STARTED, WarmupStatus.PAUSED]:
            plan.status = WarmupStatus.IN_PROGRESS
            if not plan.start_date:
                plan.start_date = datetime.now().strftime('%Y-%m-%d')
            plan.pause_reason = ""
            plan.updated_at = datetime.now().isoformat()
            self._update_next_scheduled_run(plan)
            self._save_data()
        return plan
    
    def pause_plan(self, plan_id: str, reason: str = "") -> Optional[WarmupPlan]:
        plan = self.plans.get(plan_id)
        if plan and plan.status == WarmupStatus.IN_PROGRESS:
            plan.status = WarmupStatus.PAUSED
            plan.pause_reason = reason
            plan.next_scheduled_run = ""
            plan.updated_at = datetime.now().isoformat()
            self._save_data()
        return plan
    
    def resume_plan(self, plan_id: str) -> Optional[WarmupPlan]:
        return self.start_plan(plan_id)
    
    def record_day_stats(self, plan_id: str, day: int, sent: int, delivered: int, 
                        bounced: int, complaints: int, opens: int = 0, clicks: int = 0) -> Optional[WarmupPlan]:
        plan = self.plans.get(plan_id)
        if not plan or day > len(plan.schedule):
            return None
        
        day_data = plan.schedule[day - 1]
        day_data.actual_sent = sent
        day_data.delivered = delivered
        day_data.bounced = bounced
        day_data.complaints = complaints
        day_data.opens = opens
        day_data.clicks = clicks
        day_data.date = datetime.now().strftime('%Y-%m-%d')
        day_data.send_time = datetime.now().strftime('%H:%M:%S')
        day_data.completed = True
        
        plan.total_sent += sent
        plan.total_delivered += delivered
        plan.total_bounced += bounced
        plan.total_complaints += complaints
        plan.total_opens += opens
        plan.total_clicks += clicks
        
        # Update health score and trend
        self._update_health_metrics(plan)
        
        # Check for issues and auto-pause if needed
        if plan.auto_pause_on_issues:
            if day_data.bounce_rate > plan.max_bounce_rate:
                plan.status = WarmupStatus.PAUSED
                plan.pause_reason = f"High bounce rate: {day_data.bounce_rate:.2f}% (max: {plan.max_bounce_rate}%)"
                plan.alerts.append(f"Day {day}: Paused due to high bounce rate")
            elif day_data.complaint_rate > plan.max_complaint_rate:
                plan.status = WarmupStatus.PAUSED
                plan.pause_reason = f"High complaint rate: {day_data.complaint_rate:.3f}% (max: {plan.max_complaint_rate}%)"
                plan.alerts.append(f"Day {day}: Paused due to high complaint rate")
        
        if day >= plan.total_days and plan.status == WarmupStatus.IN_PROGRESS:
            plan.status = WarmupStatus.COMPLETED
            plan.alerts.append(f"Warmup completed successfully on {datetime.now().strftime('%Y-%m-%d')}")
        else:
            plan.current_day = day + 1
            self._update_next_scheduled_run(plan)
        
        plan.last_auto_run = datetime.now().isoformat()
        plan.updated_at = datetime.now().isoformat()
        self._save_data()
        return plan
    
    def _update_health_metrics(self, plan: WarmupPlan):
        """Update health score and reputation trend based on recent performance"""
        completed_days = [d for d in plan.schedule if d.completed]
        if not completed_days:
            return
        
        # Calculate health score (0-100)
        score = 100.0
        
        # Recent days have more weight
        recent_days = completed_days[-5:] if len(completed_days) >= 5 else completed_days
        
        for day in recent_days:
            # Penalize high bounce rate
            if day.bounce_rate > 5:
                score -= 20
            elif day.bounce_rate > 3:
                score -= 10
            elif day.bounce_rate > 1:
                score -= 5
            
            # Penalize high complaint rate
            if day.complaint_rate > 0.1:
                score -= 25
            elif day.complaint_rate > 0.05:
                score -= 15
            elif day.complaint_rate > 0.01:
                score -= 5
            
            # Reward good delivery rate
            if day.delivery_rate > 98:
                score += 2
            elif day.delivery_rate > 95:
                score += 1
        
        plan.health_score = max(0, min(100, score))
        
        # Determine trend
        if len(completed_days) >= 3:
            recent_avg = sum(d.delivery_rate for d in completed_days[-3:]) / 3
            older_avg = sum(d.delivery_rate for d in completed_days[:-3]) / len(completed_days[:-3]) if len(completed_days) > 3 else recent_avg
            
            if recent_avg > older_avg + 2:
                plan.reputation_trend = "improving"
            elif recent_avg < older_avg - 2:
                plan.reputation_trend = "declining"
            else:
                plan.reputation_trend = "stable"
    
    def get_today_volume(self, plan_id: str) -> int:
        plan = self.plans.get(plan_id)
        if not plan or plan.status != WarmupStatus.IN_PROGRESS:
            return 0
        if plan.current_day > len(plan.schedule):
            return plan.target_daily_volume
        return plan.schedule[plan.current_day - 1].target_volume
    
    def get_plan(self, plan_id: str) -> Optional[WarmupPlan]:
        return self.plans.get(plan_id)
    
    def get_all_plans(self) -> List[WarmupPlan]:
        return list(self.plans.values())
    
    def get_plans_by_key(self, key_id: str) -> List[WarmupPlan]:
        return [p for p in self.plans.values() if p.key_id == key_id]
    
    def get_active_plans(self) -> List[WarmupPlan]:
        """Get all plans that are currently in progress"""
        return [p for p in self.plans.values() if p.status == WarmupStatus.IN_PROGRESS]
    
    def delete_plan(self, plan_id: str) -> bool:
        if plan_id in self.plans:
            del self.plans[plan_id]
            self._save_data()
            return True
        return False
    
    def get_stats(self) -> Dict:
        total = len(self.plans)
        in_progress = sum(1 for p in self.plans.values() if p.status == WarmupStatus.IN_PROGRESS)
        completed = sum(1 for p in self.plans.values() if p.status == WarmupStatus.COMPLETED)
        paused = sum(1 for p in self.plans.values() if p.status == WarmupStatus.PAUSED)
        failed = sum(1 for p in self.plans.values() if p.status == WarmupStatus.FAILED)
        
        # Calculate overall metrics
        total_sent = sum(p.total_sent for p in self.plans.values())
        total_delivered = sum(p.total_delivered for p in self.plans.values())
        total_bounced = sum(p.total_bounced for p in self.plans.values())
        
        return {
            'total_plans': total,
            'in_progress': in_progress,
            'completed': completed,
            'paused': paused,
            'failed': failed,
            'not_started': total - in_progress - completed - paused - failed,
            'total_emails_sent': total_sent,
            'total_delivered': total_delivered,
            'total_bounced': total_bounced,
            'overall_delivery_rate': round(total_delivered / total_sent * 100, 2) if total_sent > 0 else 0,
            'scheduler_running': self._scheduler_running
        }
    
    def get_recommendations(self, plan_id: str) -> List[Dict]:
        """Get detailed recommendations for a plan"""
        plan = self.plans.get(plan_id)
        if not plan:
            return []
        
        recommendations = []
        
        completed_days = [d for d in plan.schedule if d.completed]
        
        if completed_days:
            avg_bounce = sum(d.bounce_rate for d in completed_days) / len(completed_days)
            avg_complaint = sum(d.complaint_rate for d in completed_days) / len(completed_days)
            avg_open = sum(d.open_rate for d in completed_days) / len(completed_days)
            avg_delivery = sum(d.delivery_rate for d in completed_days) / len(completed_days)
            
            if avg_bounce > 3.0:
                recommendations.append({
                    "type": "warning",
                    "title": "High Bounce Rate",
                    "message": f"Average bounce rate is {avg_bounce:.2f}%. Consider cleaning your email list.",
                    "action": "Clean email list to remove invalid addresses"
                })
            
            if avg_complaint > 0.05:
                recommendations.append({
                    "type": "critical",
                    "title": "Elevated Complaint Rate",
                    "message": f"Complaint rate is {avg_complaint:.3f}%. This can damage sender reputation.",
                    "action": "Review email content and ensure recipients opted in"
                })
            
            if avg_open < 15.0 and len(completed_days) > 3:
                recommendations.append({
                    "type": "info",
                    "title": "Low Open Rate",
                    "message": f"Average open rate is {avg_open:.1f}%. Consider improving subject lines.",
                    "action": "A/B test different subject lines"
                })
            
            if avg_delivery < 95:
                recommendations.append({
                    "type": "warning",
                    "title": "Below Target Delivery Rate",
                    "message": f"Delivery rate is {avg_delivery:.1f}%. Target is 95%+.",
                    "action": "Check email authentication (SPF, DKIM, DMARC)"
                })
            
            if plan.status == WarmupStatus.PAUSED:
                recommendations.append({
                    "type": "critical",
                    "title": "Plan Paused",
                    "message": plan.pause_reason or "Plan is paused due to quality issues.",
                    "action": "Fix the issues before resuming the warmup"
                })
        
        if plan.status == WarmupStatus.NOT_STARTED:
            recommendations.append({
                "type": "info",
                "title": "Ready to Start",
                "message": "Your warmup plan is configured and ready.",
                "action": "Start the plan to begin building sender reputation"
            })
        
        if plan.auto_mode and not plan.recipient_list_id:
            recommendations.append({
                "type": "warning",
                "title": "No Recipient List",
                "message": "Auto mode is enabled but no recipient list is configured.",
                "action": "Select a recipient list for automatic warmup emails"
            })
        
        if plan.auto_mode and not plan.content_id:
            recommendations.append({
                "type": "warning",
                "title": "No Email Content",
                "message": "Auto mode is enabled but no email content is configured.",
                "action": "Select or create email content for warmup"
            })
        
        if plan.health_score < 50:
            recommendations.append({
                "type": "critical",
                "title": "Low Health Score",
                "message": f"Health score is {plan.health_score:.0f}/100. Sender reputation at risk.",
                "action": "Review recent sending patterns and fix issues"
            })
        
        return recommendations
    
    def get_plan_timeline(self, plan_id: str) -> List[Dict]:
        """Get timeline data for visualization"""
        plan = self.plans.get(plan_id)
        if not plan:
            return []
        
        timeline = []
        for day in plan.schedule:
            timeline.append({
                "day": day.day,
                "date": day.date or f"Day {day.day}",
                "target_volume": day.target_volume,
                "actual_sent": day.actual_sent,
                "delivered": day.delivered,
                "bounced": day.bounced,
                "complaints": day.complaints,
                "opens": day.opens,
                "clicks": day.clicks,
                "delivery_rate": round(day.delivery_rate, 2),
                "bounce_rate": round(day.bounce_rate, 2),
                "complaint_rate": round(day.complaint_rate, 3),
                "open_rate": round(day.open_rate, 2),
                "click_rate": round(day.click_rate, 2),
                "completed": day.completed,
                "status": "completed" if day.completed else ("current" if day.day == plan.current_day else "pending")
            })
        
        return timeline
    
    def get_plans_due_for_sending(self) -> List[WarmupPlan]:
        """Get plans that need to send emails now"""
        now = datetime.now()
        due_plans = []
        
        for plan in self.plans.values():
            if plan.status != WarmupStatus.IN_PROGRESS or not plan.auto_mode:
                continue
            
            # Check if it's time to send
            if plan.send_hour == now.hour and plan.send_minute <= now.minute:
                # Check if already sent today
                if plan.last_auto_run:
                    last_run = datetime.fromisoformat(plan.last_auto_run)
                    if last_run.date() == now.date():
                        continue
                
                due_plans.append(plan)
        
        return due_plans
    
    def set_send_callback(self, callback: Callable):
        """Set callback function for sending emails"""
        self._send_callback = callback
    
    async def execute_warmup_send(self, plan_id: str) -> Dict:
        """Execute warmup email sending for a plan"""
        plan = self.plans.get(plan_id)
        if not plan:
            return {"success": False, "error": "Plan not found"}
        
        if plan.status != WarmupStatus.IN_PROGRESS:
            return {"success": False, "error": f"Plan is not in progress (status: {plan.status.value})"}
        
        if not plan.recipient_list_id:
            return {"success": False, "error": "No recipient list configured"}
        
        if not plan.content_id:
            return {"success": False, "error": "No email content configured"}
        
        if not plan.from_email:
            return {"success": False, "error": "No sender email configured"}
        
        target_volume = self.get_today_volume(plan_id)
        
        # This would integrate with the actual email sending service
        # For now, return the configuration
        return {
            "success": True,
            "plan_id": plan_id,
            "day": plan.current_day,
            "target_volume": target_volume,
            "recipient_list_id": plan.recipient_list_id,
            "content_id": plan.content_id,
            "from_email": plan.from_email,
            "from_name": plan.from_name,
            "key_id": plan.key_id
        }
    
    def start_scheduler(self):
        """Start the background scheduler for automatic warmup"""
        if self._scheduler_running:
            return
        
        self._scheduler_running = True
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        print("Warmup scheduler started")
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self._scheduler_running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        print("Warmup scheduler stopped")
    
    def _scheduler_loop(self):
        """Background scheduler loop"""
        while self._scheduler_running:
            try:
                due_plans = self.get_plans_due_for_sending()
                for plan in due_plans:
                    print(f"Warmup scheduler: Plan {plan.id} is due for sending")
                    # In a real implementation, this would trigger the email sending
                    # asyncio.run(self.execute_warmup_send(plan.id))
            except Exception as e:
                print(f"Scheduler error: {e}")
            
            time.sleep(60)  # Check every minute

# Global instance
warmup_manager = SESWarmupManager()


# Алиас для совместимости с диагностикой
SESWarmupService = SESWarmupManager
WarmupManager = SESWarmupManager
