"""
SEO Monster - Advanced Bot Detection System (Keitaro-style)
"""

import os
import json
import re
import hashlib
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import random
import string

DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/tds")
BOT_DB_PATH = DATA_DIR / "bot_database.json"

BOT_SIGNATURES = {
    "search_engines": ["googlebot", "bingbot", "yandexbot", "baiduspider", "duckduckbot"],
    "social_media": ["facebookexternalhit", "twitterbot", "linkedinbot", "pinterest"],
    "seo_tools": ["semrushbot", "ahrefsbot", "mj12bot", "dotbot", "rogerbot"],
    "monitoring": ["uptimerobot", "pingdom", "statuscake", "site24x7"],
    "libraries": ["python-requests", "curl", "wget", "axios", "node-fetch"],
    "headless": ["headless", "phantom", "selenium", "puppeteer", "playwright"],
    "scrapers": ["scrapy", "nutch", "httrack", "webcopier"]
}

DATACENTER_IP_RANGES = [
    "104.16.0.0/12", "172.64.0.0/13", "45.33.0.0/17",
    "167.99.0.0/16", "35.192.0.0/12", "52.0.0.0/11"
]

SUSPICIOUS_PATTERNS = [
    r"^$", r"^-$", r"^Mozilla/[45]\.0$", r"MSIE [1-6]\."
]


@dataclass
class BotScore:
    total_score: float = 0.0
    is_bot: bool = False
    confidence: float = 0.0
    reasons: List[str] = field(default_factory=list)
    checks_passed: List[str] = field(default_factory=list)
    checks_failed: List[str] = field(default_factory=list)
    category: str = "unknown"
    recommendation: str = "allow"


@dataclass
class VisitorProfile:
    ip: str = ""
    user_agent: str = ""
    accept_language: str = ""
    accept_encoding: str = ""
    referrer: str = ""
    screen_width: int = 0
    screen_height: int = 0
    color_depth: int = 0
    timezone_offset: int = 0
    has_touch: bool = False
    has_webgl: bool = True
    has_canvas: bool = True
    plugins_count: int = 0
    languages: List[str] = field(default_factory=list)
    time_on_page: float = 0.0
    mouse_movements: int = 0
    scroll_events: int = 0
    click_events: int = 0
    fingerprint: str = ""
    canvas_hash: str = ""
    webgl_hash: str = ""


class AdvancedBotDetector:
    """Продвинутая система детекции ботов как в Keitaro"""
    
    def __init__(self):
        self.bot_database = self._load_bot_database()
        self.weights = {
            "ua_bot_signature": 100,
            "ua_suspicious_pattern": 80,
            "ua_empty": 90,
            "datacenter_ip": 60,
            "missing_headers": 50,
            "no_javascript": 85,
            "no_mouse_movement": 65,
            "fast_page_load": 55,
            "known_bot_fingerprint": 95,
            "canvas_blocked": 60,
            "webgl_blocked": 55
        }
        self.bot_threshold = 60
    
    def _load_bot_database(self) -> dict:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if BOT_DB_PATH.exists():
            try:
                with open(BOT_DB_PATH, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "known_bot_fingerprints": [],
            "known_bot_ips": [],
            "known_human_fingerprints": [],
            "detection_stats": {"total_checks": 0, "bots_detected": 0, "humans_passed": 0}
        }
    
    def _save_bot_database(self):
        with open(BOT_DB_PATH, 'w') as f:
            json.dump(self.bot_database, f, indent=2, ensure_ascii=False)
    
    def analyze_visitor(self, visitor: VisitorProfile) -> BotScore:
        """Полный анализ посетителя"""
        score = BotScore()
        
        # 1. Проверка User-Agent
        score.total_score += self._check_user_agent(visitor.user_agent, score)
        
        # 2. Проверка IP
        score.total_score += self._check_ip(visitor.ip, score)
        
        # 3. Проверка HTTP заголовков
        score.total_score += self._check_headers(visitor, score)
        
        # 4. Проверка JavaScript данных
        score.total_score += self._check_javascript_data(visitor, score)
        
        # 5. Проверка поведения
        score.total_score += self._check_behavior(visitor, score)
        
        # 6. Проверка fingerprint
        score.total_score += self._check_fingerprint(visitor, score)
        
        # Определение результата
        score.is_bot = score.total_score >= self.bot_threshold
        score.confidence = min(score.total_score / 100, 1.0)
        
        if score.total_score >= 80:
            score.recommendation = "block"
            score.category = "confirmed_bot"
        elif score.total_score >= self.bot_threshold:
            score.recommendation = "challenge"
            score.category = "suspected_bot"
        elif score.total_score >= 30:
            score.recommendation = "monitor"
            score.category = "suspicious"
        else:
            score.recommendation = "allow"
            score.category = "human"
        
        # Обновление статистики
        self.bot_database["detection_stats"]["total_checks"] += 1
        if score.is_bot:
            self.bot_database["detection_stats"]["bots_detected"] += 1
        else:
            self.bot_database["detection_stats"]["humans_passed"] += 1
        
        return score
    
    def _check_user_agent(self, ua: str, score: BotScore) -> float:
        points = 0
        ua_lower = ua.lower() if ua else ""
        
        if not ua or ua.strip() == "":
            score.checks_failed.append("empty_user_agent")
            score.reasons.append("Empty User-Agent")
            return self.weights["ua_empty"]
        
        for category, signatures in BOT_SIGNATURES.items():
            for sig in signatures:
                if sig in ua_lower:
                    score.checks_failed.append(f"bot_signature_{category}")
                    score.reasons.append(f"Bot signature: {sig} ({category})")
                    score.category = category
                    return self.weights["ua_bot_signature"]
        
        for pattern in SUSPICIOUS_PATTERNS:
            if re.match(pattern, ua, re.IGNORECASE):
                score.checks_failed.append("suspicious_ua_pattern")
                score.reasons.append(f"Suspicious UA pattern")
                points += self.weights["ua_suspicious_pattern"]
                break
        
        if points == 0:
            score.checks_passed.append("user_agent_clean")
        return points
    
    def _check_ip(self, ip: str, score: BotScore) -> float:
        points = 0
        if not ip:
            return 0
        
        try:
            ip_obj = ipaddress.ip_address(ip)
            for dc_range in DATACENTER_IP_RANGES:
                if ip_obj in ipaddress.ip_network(dc_range, strict=False):
                    score.checks_failed.append("datacenter_ip")
                    score.reasons.append(f"Datacenter IP: {dc_range}")
                    points += self.weights["datacenter_ip"]
                    break
        except:
            pass
        
        if ip in self.bot_database.get("known_bot_ips", []):
            score.checks_failed.append("known_bot_ip")
            score.reasons.append("Known bot IP")
            points += 50
        
        if points == 0:
            score.checks_passed.append("ip_clean")
        return points
    
    def _check_headers(self, visitor: VisitorProfile, score: BotScore) -> float:
        points = 0
        
        if not visitor.accept_language:
            score.checks_failed.append("missing_accept_language")
            score.reasons.append("Missing Accept-Language")
            points += self.weights["missing_headers"] * 0.5
        else:
            score.checks_passed.append("has_accept_language")
        
        if not visitor.accept_encoding:
            score.checks_failed.append("missing_accept_encoding")
            points += self.weights["missing_headers"] * 0.3
        
        return points
    
    def _check_javascript_data(self, visitor: VisitorProfile, score: BotScore) -> float:
        points = 0
        
        if visitor.screen_width == 0 or visitor.screen_height == 0:
            score.checks_failed.append("no_screen_data")
            score.reasons.append("No screen data (JS disabled?)")
            points += self.weights["no_javascript"]
        else:
            score.checks_passed.append("has_screen_data")
            if visitor.screen_width < 320 or visitor.screen_height < 240:
                score.checks_failed.append("unusual_screen_size")
                points += 30
        
        if not visitor.has_canvas:
            score.checks_failed.append("canvas_blocked")
            points += self.weights["canvas_blocked"]
        
        if not visitor.has_webgl:
            score.checks_failed.append("webgl_blocked")
            points += self.weights["webgl_blocked"]
        
        return points
    
    def _check_behavior(self, visitor: VisitorProfile, score: BotScore) -> float:
        points = 0
        
        if visitor.time_on_page > 0 and visitor.time_on_page < 0.5:
            score.checks_failed.append("too_fast")
            score.reasons.append(f"Too fast: {visitor.time_on_page}s")
            points += self.weights["fast_page_load"]
        
        if visitor.time_on_page > 2 and visitor.mouse_movements == 0:
            score.checks_failed.append("no_mouse_movement")
            score.reasons.append("No mouse movement")
            points += self.weights["no_mouse_movement"]
        elif visitor.mouse_movements > 0:
            score.checks_passed.append("has_mouse_movement")
        
        return points
    
    def _check_fingerprint(self, visitor: VisitorProfile, score: BotScore) -> float:
        points = 0
        if not visitor.fingerprint:
            return 0
        
        if visitor.fingerprint in self.bot_database.get("known_bot_fingerprints", []):
            score.checks_failed.append("known_bot_fingerprint")
            score.reasons.append("Known bot fingerprint")
            points += self.weights["known_bot_fingerprint"]
        elif visitor.fingerprint in self.bot_database.get("known_human_fingerprints", []):
            score.checks_passed.append("known_human_fingerprint")
            points -= 30
        
        return max(0, points)
    
    def mark_as_bot(self, fingerprint: str, ip: str = ""):
        if fingerprint and fingerprint not in self.bot_database["known_bot_fingerprints"]:
            self.bot_database["known_bot_fingerprints"].append(fingerprint)
        if ip and ip not in self.bot_database["known_bot_ips"]:
            self.bot_database["known_bot_ips"].append(ip)
        self._save_bot_database()
    
    def mark_as_human(self, fingerprint: str):
        if fingerprint and fingerprint not in self.bot_database["known_human_fingerprints"]:
            self.bot_database["known_human_fingerprints"].append(fingerprint)
            if fingerprint in self.bot_database["known_bot_fingerprints"]:
                self.bot_database["known_bot_fingerprints"].remove(fingerprint)
        self._save_bot_database()
    
    def get_stats(self) -> Dict:
        stats = self.bot_database.get("detection_stats", {})
        total = stats.get("total_checks", 0)
        bots = stats.get("bots_detected", 0)
        return {
            "total_checks": total,
            "bots_detected": bots,
            "humans_passed": stats.get("humans_passed", 0),
            "bot_rate": (bots / total * 100) if total > 0 else 0,
            "known_bot_fingerprints": len(self.bot_database.get("known_bot_fingerprints", [])),
            "known_bot_ips": len(self.bot_database.get("known_bot_ips", [])),
            "known_human_fingerprints": len(self.bot_database.get("known_human_fingerprints", []))
        }
    
    def generate_js_challenge(self) -> str:
        challenge_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return f'''
(function(){{
    var c={{id:"{challenge_id}",ts:Date.now(),sw:screen.width,sh:screen.height,
    cd:screen.colorDepth,tz:new Date().getTimezoneOffset(),
    touch:'ontouchstart' in window,
    webgl:(function(){{try{{var cv=document.createElement('canvas');
    return !!(cv.getContext('webgl')||cv.getContext('experimental-webgl'));}}catch(e){{return false;}}}}()),
    canvas:(function(){{try{{return !!document.createElement('canvas').getContext('2d');}}catch(e){{return false;}}}}()),
    plugins:navigator.plugins.length,langs:navigator.languages||[navigator.language],mm:0,sc:0,cl:0}};
    document.addEventListener('mousemove',function(){{c.mm++;}});
    document.addEventListener('scroll',function(){{c.sc++;}});
    document.addEventListener('click',function(){{c.cl++;}});
    window.__botCheck=c;
    setTimeout(function(){{c.top=Date.now()-c.ts;
    var img=new Image();img.src='/api/tds/verify?d='+btoa(JSON.stringify(c));}},2000);
}})();'''


bot_detector = AdvancedBotDetector()
