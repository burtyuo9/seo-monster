#!/usr/bin/env python3
"""
SEO Monster - Daily SEO Report Script
Скрипт для автоматической отправки ежедневных отчётов по индексации и позициям в Telegram

Использование:
    python3 daily_indexing_report.py              # Отправить отчёт сейчас
    python3 daily_indexing_report.py --setup-cron # Настроить cron для ежедневной отправки
    python3 daily_indexing_report.py --test       # Тестовый запуск (без отправки)
    python3 daily_indexing_report.py --preview    # Предпросмотр отчёта
    python3 daily_indexing_report.py --check-positions  # Проверить позиции перед отчётом

Для работы требуется:
    1. Настроенный Telegram бот в SEO Monster
    2. Хотя бы один подписчик бота
"""

import os
import sys
import json
import asyncio
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Добавляем путь к backend
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    import aiohttp
except ImportError:
    print("Установка aiohttp...")
    os.system("pip3 install aiohttp")
    import aiohttp


# Конфигурация
DATA_DIR = Path(__file__).parent.parent / "backend" / "data"
INDEXING_DIR = DATA_DIR / "indexing"
TELEGRAM_DIR = DATA_DIR / "telegram"
POSITIONS_DIR = DATA_DIR / "positions"

API_BASE = "http://localhost:8000"


class SEOReportGenerator:
    """Генератор полных SEO-отчётов"""
    
    def __init__(self):
        self.indexing_history = self._load_indexing_history()
        self.telegram_config = self._load_telegram_config()
        self.keywords = self._load_keywords()
        self.position_history = self._load_position_history()
        
    def _load_indexing_history(self) -> List[Dict]:
        """Загрузка истории индексации"""
        history_file = INDEXING_DIR / "indexing_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _load_telegram_config(self) -> Dict:
        """Загрузка конфигурации Telegram"""
        config_file = TELEGRAM_DIR / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _load_subscribers(self) -> List[Dict]:
        """Загрузка подписчиков"""
        subscribers_file = TELEGRAM_DIR / "subscribers.json"
        if subscribers_file.exists():
            try:
                with open(subscribers_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _load_keywords(self) -> List[Dict]:
        """Загрузка ключевых слов"""
        keywords_file = POSITIONS_DIR / "keywords.json"
        if keywords_file.exists():
            try:
                with open(keywords_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _load_position_history(self) -> List[Dict]:
        """Загрузка истории позиций"""
        history_file = POSITIONS_DIR / "position_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def get_today_indexing_stats(self) -> Dict:
        """Получение статистики индексации за сегодня"""
        today = datetime.now().date()
        
        stats = {
            "total_submitted": 0,
            "google_submitted": 0,
            "bing_submitted": 0,
            "yandex_submitted": 0,
            "successful": 0,
            "failed": 0,
            "domains": {},
        }
        
        for entry in self.indexing_history:
            try:
                entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                if entry_time.date() == today:
                    stats["total_submitted"] += 1
                    
                    engines = entry.get("search_engines", [])
                    if "google" in engines:
                        stats["google_submitted"] += 1
                    if "bing" in engines:
                        stats["bing_submitted"] += 1
                    if "yandex" in engines:
                        stats["yandex_submitted"] += 1
                    
                    if entry.get("status") == "success":
                        stats["successful"] += 1
                    else:
                        stats["failed"] += 1
                    
                    url = entry.get("url", "")
                    if url:
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(url).netloc
                            if domain:
                                stats["domains"][domain] = stats["domains"].get(domain, 0) + 1
                        except:
                            pass
            except:
                continue
        
        return stats
    
    def get_weekly_indexing_stats(self) -> Dict:
        """Получение статистики индексации за неделю"""
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        stats = {
            "total": 0,
            "by_day": {},
            "top_domains": {}
        }
        
        for entry in self.indexing_history:
            try:
                entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                entry_date = entry_time.date()
                
                if week_ago <= entry_date <= today:
                    stats["total"] += 1
                    
                    day_str = entry_date.strftime("%d.%m")
                    stats["by_day"][day_str] = stats["by_day"].get(day_str, 0) + 1
                    
                    url = entry.get("url", "")
                    if url:
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(url).netloc
                            if domain:
                                stats["top_domains"][domain] = stats["top_domains"].get(domain, 0) + 1
                        except:
                            pass
            except:
                continue
        
        return stats
    
    def get_pending_urls(self) -> List[Dict]:
        """Получение URL в очереди на индексацию"""
        queue_file = INDEXING_DIR / "indexing_queue.json"
        if queue_file.exists():
            try:
                with open(queue_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def get_position_summary(self) -> Dict:
        """Получение сводки по позициям"""
        summary = {
            "total_keywords": len(self.keywords),
            "google": {"top_3": 0, "top_10": 0, "top_30": 0, "top_100": 0, "not_found": 0},
            "bing": {"top_3": 0, "top_10": 0, "top_30": 0, "top_100": 0, "not_found": 0},
            "improved": 0,
            "declined": 0,
            "stable": 0
        }
        
        for kw in self.keywords:
            # Google
            g_pos = kw.get("google_position")
            if g_pos is None:
                summary["google"]["not_found"] += 1
            elif g_pos <= 3:
                summary["google"]["top_3"] += 1
            elif g_pos <= 10:
                summary["google"]["top_10"] += 1
            elif g_pos <= 30:
                summary["google"]["top_30"] += 1
            elif g_pos <= 100:
                summary["google"]["top_100"] += 1
            else:
                summary["google"]["not_found"] += 1
            
            # Bing
            b_pos = kw.get("bing_position")
            if b_pos is None:
                summary["bing"]["not_found"] += 1
            elif b_pos <= 3:
                summary["bing"]["top_3"] += 1
            elif b_pos <= 10:
                summary["bing"]["top_10"] += 1
            elif b_pos <= 30:
                summary["bing"]["top_30"] += 1
            elif b_pos <= 100:
                summary["bing"]["top_100"] += 1
            else:
                summary["bing"]["not_found"] += 1
        
        # Подсчёт изменений
        today = datetime.now().date()
        for h in self.position_history:
            try:
                h_date = datetime.fromisoformat(h.get("timestamp", "")).date()
                if h_date == today:
                    g_change = h.get("google_change")
                    if g_change is not None:
                        if g_change > 0:
                            summary["improved"] += 1
                        elif g_change < 0:
                            summary["declined"] += 1
                        else:
                            summary["stable"] += 1
            except:
                continue
        
        return summary
    
    def get_top_keywords(self, limit: int = 10) -> List[Dict]:
        """Получение топ ключевых слов по позициям"""
        sorted_keywords = sorted(
            self.keywords,
            key=lambda x: (x.get("google_position") or 999, x.get("bing_position") or 999)
        )
        
        result = []
        for kw in sorted_keywords[:limit]:
            # Ищем изменение в истории
            change = None
            for h in reversed(self.position_history[-100:]):
                if h.get("keyword_id") == kw.get("id"):
                    change = h.get("google_change")
                    break
            
            result.append({
                "keyword": kw["keyword"],
                "domain": kw.get("domain", ""),
                "google_position": kw.get("google_position"),
                "bing_position": kw.get("bing_position"),
                "change": change
            })
        
        return result
    
    def generate_report(self) -> str:
        """Генерация полного отчёта"""
        today_stats = self.get_today_indexing_stats()
        weekly_stats = self.get_weekly_indexing_stats()
        pending = self.get_pending_urls()
        position_summary = self.get_position_summary()
        top_keywords = self.get_top_keywords(10)
        
        # Заголовок
        report = f"""
📊 <b>Ежедневный SEO-отчёт</b>
📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}

"""
        
        # ═══════════════════════════════════════
        # СЕКЦИЯ: ПОЗИЦИИ В ПОИСКОВИКАХ
        # ═══════════════════════════════════════
        
        report += "━━━━━━━━━━━━━━━━━━━━━━\n"
        report += "🎯 <b>ПОЗИЦИИ В ПОИСКОВИКАХ</b>\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        if self.keywords:
            # Сводка по Google
            g = position_summary["google"]
            report += f"""<b>Google:</b>
  🥇 Топ-3: {g['top_3']}
  🥈 Топ-10: {g['top_10']}
  🥉 Топ-30: {g['top_30']}
  📍 Топ-100: {g['top_100']}
  ❓ Не найдено: {g['not_found']}

"""
            
            # Сводка по Bing
            b = position_summary["bing"]
            report += f"""<b>Bing:</b>
  🥇 Топ-3: {b['top_3']}
  🥈 Топ-10: {b['top_10']}
  🥉 Топ-30: {b['top_30']}
  📍 Топ-100: {b['top_100']}
  ❓ Не найдено: {b['not_found']}

"""
            
            # Изменения за сегодня
            if position_summary["improved"] or position_summary["declined"]:
                report += f"""<b>Изменения сегодня:</b>
  📈 Выросли: {position_summary['improved']}
  📉 Упали: {position_summary['declined']}
  ➡️ Без изменений: {position_summary['stable']}

"""
            
            # Топ ключевые слова
            if top_keywords:
                report += "<b>Ключевые слова:</b>\n"
                report += "<code>"
                report += f"{'Ключ':<20} {'G':>4} {'B':>4} {'Δ':>3}\n"
                report += "─" * 33 + "\n"
                
                for kw in top_keywords:
                    keyword = kw["keyword"][:18]
                    g_pos = str(kw["google_position"]) if kw["google_position"] else "—"
                    b_pos = str(kw["bing_position"]) if kw["bing_position"] else "—"
                    
                    change = kw.get("change")
                    if change is not None:
                        if change > 0:
                            change_str = f"+{change}"
                        elif change < 0:
                            change_str = str(change)
                        else:
                            change_str = "="
                    else:
                        change_str = "—"
                    
                    report += f"{keyword:<20} {g_pos:>4} {b_pos:>4} {change_str:>3}\n"
                
                report += "</code>\n"
                report += f"\n<i>G = Google, B = Bing, Δ = изменение</i>\n"
        else:
            report += "<i>Ключевые слова не настроены.</i>\n"
            report += "<i>Добавьте их в разделе \"Позиции\" веб-интерфейса.</i>\n"
        
        # ═══════════════════════════════════════
        # СЕКЦИЯ: ИНДЕКСАЦИЯ
        # ═══════════════════════════════════════
        
        report += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        report += "🔍 <b>ИНДЕКСАЦИЯ</b>\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        report += f"""<b>Сегодня отправлено:</b> {today_stats['total_submitted']} URL

<b>По поисковикам:</b>
  🔵 Google: {today_stats['google_submitted']}
  🟠 Bing: {today_stats['bing_submitted']}
  🔴 Yandex: {today_stats['yandex_submitted']}

<b>Результат:</b>
  ✅ Успешно: {today_stats['successful']}
  ❌ Ошибок: {today_stats['failed']}
"""
        
        # Топ доменов за сегодня
        if today_stats['domains']:
            report += "\n<b>Домены сегодня:</b>\n"
            sorted_domains = sorted(today_stats['domains'].items(), key=lambda x: x[1], reverse=True)[:5]
            for domain, count in sorted_domains:
                report += f"  • {domain}: {count}\n"
        
        # Статистика за неделю
        report += f"\n<b>За 7 дней:</b> {weekly_stats['total']} URL\n"
        
        # График по дням
        if weekly_stats['by_day']:
            report += "\n<b>По дням:</b>\n"
            max_count = max(weekly_stats['by_day'].values()) if weekly_stats['by_day'] else 1
            for day, count in sorted(weekly_stats['by_day'].items()):
                bar_length = int((count / max_count) * 8)
                bar = "█" * bar_length + "░" * (8 - bar_length)
                report += f"  {day}: {bar} {count}\n"
        
        # Очередь
        pending_count = len(pending)
        report += f"\n<b>В очереди:</b> {pending_count} URL\n"
        
        # ═══════════════════════════════════════
        # ФУТЕР
        # ═══════════════════════════════════════
        
        report += """
━━━━━━━━━━━━━━━━━━━━━━

💡 <i>Отчёт сгенерирован автоматически</i>
🤖 <i>SEO Monster</i>
"""
        
        return report
    
    async def send_report(self, test_mode: bool = False) -> Dict:
        """Отправка отчёта в Telegram"""
        if not self.telegram_config.get("bot_token"):
            return {"error": "Telegram bot token not configured"}
        
        if not self.telegram_config.get("enabled"):
            return {"error": "Telegram bot is disabled"}
        
        subscribers = self._load_subscribers()
        if not subscribers:
            return {"error": "No subscribers"}
        
        report = self.generate_report()
        
        if test_mode:
            print("\n" + "="*50)
            print("ТЕСТОВЫЙ РЕЖИМ - Отчёт не будет отправлен")
            print("="*50)
            clean = report.replace("<b>", "").replace("</b>", "")
            clean = clean.replace("<i>", "").replace("</i>", "")
            clean = clean.replace("<code>", "").replace("</code>", "")
            print(clean)
            return {"status": "test", "report_length": len(report)}
        
        # Отправка
        results = []
        bot_token = self.telegram_config["bot_token"]
        
        async with aiohttp.ClientSession() as session:
            for subscriber in subscribers:
                chat_id = subscriber.get("chat_id")
                if not chat_id:
                    continue
                
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": report,
                    "parse_mode": "HTML"
                }
                
                try:
                    async with session.post(url, json=payload) as response:
                        result = await response.json()
                        results.append({
                            "chat_id": chat_id,
                            "success": result.get("ok", False)
                        })
                except Exception as e:
                    results.append({
                        "chat_id": chat_id,
                        "success": False,
                        "error": str(e)
                    })
        
        self._log_report_sent(results)
        
        sent = len([r for r in results if r["success"]])
        failed = len([r for r in results if not r["success"]])
        
        return {"status": "sent", "sent": sent, "failed": failed, "results": results}
    
    def _log_report_sent(self, results: List[Dict]):
        """Логирование отправки"""
        log_file = TELEGRAM_DIR / "report_log.json"
        
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except:
                pass
        
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "type": "daily_seo_report",
            "results": results
        })
        
        logs = logs[-100:]
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)


async def check_positions():
    """Проверка позиций перед отчётом"""
    print("🔍 Проверка позиций...")
    
    try:
        from services.position_tracker import get_position_tracker
        tracker = get_position_tracker()
        
        keywords = tracker.get_keywords()
        if not keywords:
            print("⚠️  Нет ключевых слов для проверки")
            return
        
        print(f"📊 Проверяем {len(keywords)} ключевых слов...")
        results = await tracker.check_all_positions()
        
        print(f"✅ Проверено: {len(results)} ключевых слов")
        
        for r in results[:5]:
            kw = r["keyword"][:20]
            g = r.get("google_position") or "—"
            b = r.get("bing_position") or "—"
            print(f"   • {kw}: G:{g} B:{b}")
        
        if len(results) > 5:
            print(f"   ... и ещё {len(results) - 5}")
            
    except Exception as e:
        print(f"❌ Ошибка проверки позиций: {e}")


def setup_cron():
    """Настройка cron"""
    script_path = Path(__file__).resolve()
    
    cron_command = f"0 9 * * * cd {script_path.parent.parent} && /usr/bin/python3 {script_path}"
    
    print("📋 Для настройки ежедневной отправки отчётов:")
    print()
    print("1. Откройте crontab:")
    print("   crontab -e")
    print()
    print("2. Добавьте строку:")
    print(f"   {cron_command}")
    print()
    print("3. Сохраните и закройте редактор")
    print()
    print("Отчёт будет отправляться каждый день в 9:00")
    print()
    print("Для проверки позиций перед отчётом добавьте:")
    print(f"   0 8 * * * cd {script_path.parent.parent} && /usr/bin/python3 {script_path} --check-positions")
    print()


async def main():
    parser = argparse.ArgumentParser(description='SEO Monster - Daily SEO Report')
    parser.add_argument('--test', action='store_true', help='Тестовый режим')
    parser.add_argument('--setup-cron', action='store_true', help='Настроить cron')
    parser.add_argument('--preview', action='store_true', help='Предпросмотр')
    parser.add_argument('--check-positions', action='store_true', help='Проверить позиции')
    
    args = parser.parse_args()
    
    if args.setup_cron:
        setup_cron()
        return
    
    print("🔍 SEO Monster - Daily SEO Report")
    print("="*40)
    
    if args.check_positions:
        await check_positions()
        return
    
    generator = SEOReportGenerator()
    
    if args.preview:
        report = generator.generate_report()
        print("\n📋 Предпросмотр отчёта:\n")
        clean = report.replace("<b>", "").replace("</b>", "")
        clean = clean.replace("<i>", "").replace("</i>", "")
        clean = clean.replace("<code>", "").replace("</code>", "")
        print(clean)
        return
    
    print("📊 Генерация отчёта...")
    
    result = await generator.send_report(test_mode=args.test)
    
    if "error" in result:
        print(f"❌ Ошибка: {result['error']}")
        sys.exit(1)
    elif result.get("status") == "test":
        print(f"\n✅ Тест успешен! Длина отчёта: {result['report_length']} символов")
    else:
        print(f"\n✅ Отчёт отправлен!")
        print(f"   Успешно: {result['sent']}")
        print(f"   Ошибок: {result['failed']}")


if __name__ == "__main__":
    asyncio.run(main())
