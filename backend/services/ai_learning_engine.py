"""
SEO Monster - AI Learning Engine
Движок самообучения AI-агента

Возможности:
- Анализ результатов SEO-кампаний
- Выявление успешных паттернов
- Оптимизация стратегий на основе данных
- Адаптация под изменения алгоритмов поисковиков
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict

# Пути
DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data")
LEARNING_DIR = DATA_DIR / "learning"
LEARNING_DIR.mkdir(parents=True, exist_ok=True)

# Файлы
SEO_PATTERNS_FILE = LEARNING_DIR / "seo_patterns.json"
STRATEGY_SCORES_FILE = LEARNING_DIR / "strategy_scores.json"
CONTENT_ANALYSIS_FILE = LEARNING_DIR / "content_analysis.json"
PLATFORM_STATS_FILE = LEARNING_DIR / "platform_stats.json"
OPTIMIZATION_LOG_FILE = LEARNING_DIR / "optimization_log.json"


class SEOLearningEngine:
    """
    Движок самообучения для SEO-оптимизации
    Анализирует результаты и улучшает стратегии
    """
    
    def __init__(self):
        self.seo_patterns = self._load_json(SEO_PATTERNS_FILE, {"patterns": [], "keywords": {}, "content_types": {}})
        self.strategy_scores = self._load_json(STRATEGY_SCORES_FILE, {"strategies": {}, "history": []})
        self.content_analysis = self._load_json(CONTENT_ANALYSIS_FILE, {"successful": [], "failed": [], "templates": []})
        self.platform_stats = self._load_json(PLATFORM_STATS_FILE, {"platforms": {}, "best_times": {}, "engagement": {}})
    
    def _load_json(self, path: Path, default: Dict) -> Dict:
        """Загрузка JSON файла"""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default
    
    def _save_json(self, path: Path, data: Dict):
        """Сохранение JSON файла"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ═══════════════════════════════════════════════════════════════
    # АНАЛИЗ РЕЗУЛЬТАТОВ
    # ═══════════════════════════════════════════════════════════════
    
    def analyze_campaign_results(self, campaign_data: Dict) -> Dict:
        """
        Анализ результатов SEO-кампании
        Выявляет что сработало, а что нет
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "campaign_id": campaign_data.get("id"),
            "domain": campaign_data.get("domain"),
            "metrics": {},
            "insights": [],
            "recommendations": []
        }
        
        # Анализ позиций
        positions = campaign_data.get("positions", {})
        if positions:
            avg_position = sum(p for p in positions.values() if p) / max(len([p for p in positions.values() if p]), 1)
            top_10_count = len([p for p in positions.values() if p and p <= 10])
            
            analysis["metrics"]["avg_position"] = round(avg_position, 2)
            analysis["metrics"]["top_10_keywords"] = top_10_count
            analysis["metrics"]["total_keywords"] = len(positions)
            
            if avg_position <= 10:
                analysis["insights"].append("Отличные позиции! Средняя позиция в топ-10")
            elif avg_position <= 30:
                analysis["insights"].append("Хорошие позиции, есть потенциал для роста")
            else:
                analysis["insights"].append("Позиции требуют улучшения")
        
        # Анализ контента
        content_stats = campaign_data.get("content", {})
        if content_stats:
            total_content = content_stats.get("total", 0)
            published = content_stats.get("published", 0)
            engagement = content_stats.get("engagement", 0)
            
            analysis["metrics"]["content_published"] = published
            analysis["metrics"]["engagement_rate"] = round(engagement / max(published, 1), 2)
            
            if engagement / max(published, 1) > 0.1:
                analysis["insights"].append("Высокая вовлечённость контента")
        
        # Анализ ссылок
        links = campaign_data.get("links", {})
        if links:
            total_links = links.get("total", 0)
            quality_links = links.get("quality", 0)
            
            analysis["metrics"]["total_links"] = total_links
            analysis["metrics"]["quality_ratio"] = round(quality_links / max(total_links, 1), 2)
        
        # Генерация рекомендаций
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        # Сохраняем для обучения
        self._learn_from_campaign(analysis)
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация рекомендаций на основе анализа"""
        recommendations = []
        metrics = analysis.get("metrics", {})
        
        # Рекомендации по позициям
        avg_pos = metrics.get("avg_position", 100)
        if avg_pos > 30:
            recommendations.append("Увеличить количество качественного контента")
            recommendations.append("Усилить внутреннюю перелинковку")
        elif avg_pos > 10:
            recommendations.append("Оптимизировать существующий контент под ключевые слова")
            recommendations.append("Добавить больше внешних ссылок")
        
        # Рекомендации по контенту
        engagement = metrics.get("engagement_rate", 0)
        if engagement < 0.05:
            recommendations.append("Улучшить качество заголовков")
            recommendations.append("Добавить больше визуального контента")
        
        # Рекомендации по ссылкам
        quality_ratio = metrics.get("quality_ratio", 0)
        if quality_ratio < 0.3:
            recommendations.append("Сфокусироваться на качественных площадках")
            recommendations.append("Уменьшить количество низкокачественных ссылок")
        
        return recommendations
    
    def _learn_from_campaign(self, analysis: Dict):
        """Обучение на результатах кампании"""
        # Определяем успешность
        metrics = analysis.get("metrics", {})
        avg_pos = metrics.get("avg_position", 100)
        engagement = metrics.get("engagement_rate", 0)
        
        success_score = 0
        if avg_pos <= 10:
            success_score += 50
        elif avg_pos <= 30:
            success_score += 30
        elif avg_pos <= 50:
            success_score += 10
        
        if engagement > 0.1:
            success_score += 30
        elif engagement > 0.05:
            success_score += 15
        
        # Сохраняем паттерн
        pattern = {
            "timestamp": analysis.get("timestamp"),
            "domain": analysis.get("domain"),
            "success_score": success_score,
            "metrics": metrics,
            "insights": analysis.get("insights", [])
        }
        
        self.seo_patterns["patterns"].append(pattern)
        self.seo_patterns["patterns"] = self.seo_patterns["patterns"][-500:]
        self._save_json(SEO_PATTERNS_FILE, self.seo_patterns)
    
    # ═══════════════════════════════════════════════════════════════
    # АНАЛИЗ КОНТЕНТА
    # ═══════════════════════════════════════════════════════════════
    
    def analyze_content_performance(self, content_list: List[Dict]) -> Dict:
        """
        Анализ эффективности контента
        Выявляет успешные шаблоны
        """
        analysis = {
            "total_analyzed": len(content_list),
            "successful_patterns": [],
            "failed_patterns": [],
            "best_practices": [],
            "optimal_length": None,
            "best_keywords_density": None
        }
        
        successful = []
        failed = []
        
        for content in content_list:
            performance = content.get("performance", {})
            views = performance.get("views", 0)
            engagement = performance.get("engagement", 0)
            conversions = performance.get("conversions", 0)
            
            # Оценка успешности
            score = views * 0.3 + engagement * 0.5 + conversions * 0.2
            
            content_data = {
                "title_length": len(content.get("title", "")),
                "content_length": len(content.get("content", "")),
                "has_images": content.get("has_images", False),
                "has_video": content.get("has_video", False),
                "keywords_count": content.get("keywords_count", 0),
                "score": score
            }
            
            if score > 50:
                successful.append(content_data)
            else:
                failed.append(content_data)
        
        # Анализ успешных паттернов
        if successful:
            avg_title_len = sum(c["title_length"] for c in successful) / len(successful)
            avg_content_len = sum(c["content_length"] for c in successful) / len(successful)
            images_ratio = len([c for c in successful if c["has_images"]]) / len(successful)
            
            analysis["successful_patterns"] = {
                "avg_title_length": round(avg_title_len),
                "avg_content_length": round(avg_content_len),
                "images_usage": round(images_ratio * 100),
                "count": len(successful)
            }
            
            analysis["optimal_length"] = round(avg_content_len)
            
            # Best practices
            if images_ratio > 0.7:
                analysis["best_practices"].append("Использовать изображения в контенте")
            if avg_title_len < 60:
                analysis["best_practices"].append(f"Оптимальная длина заголовка: {round(avg_title_len)} символов")
            if avg_content_len > 1000:
                analysis["best_practices"].append("Длинный контент показывает лучшие результаты")
        
        # Сохраняем для обучения
        self.content_analysis["successful"].extend(successful[-50:])
        self.content_analysis["failed"].extend(failed[-50:])
        self.content_analysis["successful"] = self.content_analysis["successful"][-200:]
        self.content_analysis["failed"] = self.content_analysis["failed"][-200:]
        self._save_json(CONTENT_ANALYSIS_FILE, self.content_analysis)
        
        return analysis
    
    def get_content_recommendations(self, topic: str, target_platform: str = None) -> Dict:
        """
        Получение рекомендаций для создания контента
        На основе обученных паттернов
        """
        recommendations = {
            "topic": topic,
            "platform": target_platform,
            "title_recommendations": [],
            "content_structure": [],
            "optimal_length": 1500,
            "keywords_to_include": [],
            "media_recommendations": []
        }
        
        # Анализируем успешный контент
        successful = self.content_analysis.get("successful", [])
        if successful:
            avg_length = sum(c.get("content_length", 1500) for c in successful) / len(successful)
            recommendations["optimal_length"] = round(avg_length)
            
            images_ratio = len([c for c in successful if c.get("has_images")]) / max(len(successful), 1)
            if images_ratio > 0.5:
                recommendations["media_recommendations"].append("Добавить 2-3 изображения")
        
        # Рекомендации по заголовку
        recommendations["title_recommendations"] = [
            "Использовать числа в заголовке (например, '10 способов...')",
            "Длина заголовка: 50-60 символов",
            "Включить основное ключевое слово"
        ]
        
        # Структура контента
        recommendations["content_structure"] = [
            "Введение (100-150 слов)",
            "Основная часть с подзаголовками H2/H3",
            "Списки и буллеты для лучшего восприятия",
            "Заключение с призывом к действию"
        ]
        
        # Платформо-специфичные рекомендации
        platform_data = self.platform_stats.get("platforms", {}).get(target_platform, {})
        if platform_data:
            if platform_data.get("best_length"):
                recommendations["optimal_length"] = platform_data["best_length"]
            if platform_data.get("best_time"):
                recommendations["best_posting_time"] = platform_data["best_time"]
        
        return recommendations
    
    # ═══════════════════════════════════════════════════════════════
    # АНАЛИЗ ПЛАТФОРМ
    # ═══════════════════════════════════════════════════════════════
    
    def analyze_platform_performance(self, platform: str, posts: List[Dict]) -> Dict:
        """
        Анализ эффективности платформы
        """
        analysis = {
            "platform": platform,
            "total_posts": len(posts),
            "avg_engagement": 0,
            "best_posting_times": [],
            "best_content_types": [],
            "recommendations": []
        }
        
        if not posts:
            return analysis
        
        # Анализ вовлечённости
        engagements = [p.get("engagement", 0) for p in posts]
        analysis["avg_engagement"] = round(sum(engagements) / len(engagements), 2)
        
        # Анализ времени публикации
        time_engagement = defaultdict(list)
        for post in posts:
            post_time = post.get("posted_at", "")
            if post_time:
                try:
                    hour = datetime.fromisoformat(post_time).hour
                    time_engagement[hour].append(post.get("engagement", 0))
                except:
                    pass
        
        # Лучшее время
        best_hours = sorted(
            time_engagement.items(),
            key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
            reverse=True
        )[:3]
        analysis["best_posting_times"] = [f"{h}:00" for h, _ in best_hours]
        
        # Сохраняем статистику платформы
        self.platform_stats["platforms"][platform] = {
            "avg_engagement": analysis["avg_engagement"],
            "best_times": analysis["best_posting_times"],
            "total_posts": len(posts),
            "last_updated": datetime.now().isoformat()
        }
        self._save_json(PLATFORM_STATS_FILE, self.platform_stats)
        
        return analysis
    
    # ═══════════════════════════════════════════════════════════════
    # ОПТИМИЗАЦИЯ СТРАТЕГИЙ
    # ═══════════════════════════════════════════════════════════════
    
    def optimize_strategy(self, current_strategy: Dict) -> Dict:
        """
        Оптимизация SEO-стратегии на основе обученных данных
        """
        optimized = current_strategy.copy()
        
        # Анализируем успешные паттерны
        patterns = self.seo_patterns.get("patterns", [])
        successful_patterns = [p for p in patterns if p.get("success_score", 0) > 50]
        
        if successful_patterns:
            # Извлекаем лучшие практики
            for pattern in successful_patterns[-20:]:
                metrics = pattern.get("metrics", {})
                
                # Оптимизация частоты публикаций
                if metrics.get("content_published", 0) > 10:
                    optimized["content_frequency"] = "high"
                
                # Оптимизация качества ссылок
                if metrics.get("quality_ratio", 0) > 0.5:
                    optimized["link_quality_focus"] = True
        
        # Добавляем рекомендации
        optimized["optimizations_applied"] = []
        
        # Анализ контента
        content_data = self.content_analysis.get("successful", [])
        if content_data:
            avg_length = sum(c.get("content_length", 1500) for c in content_data) / len(content_data)
            optimized["recommended_content_length"] = round(avg_length)
            optimized["optimizations_applied"].append(f"Оптимальная длина контента: {round(avg_length)} символов")
        
        # Анализ платформ
        platforms = self.platform_stats.get("platforms", {})
        best_platform = max(platforms.items(), key=lambda x: x[1].get("avg_engagement", 0), default=(None, {}))
        if best_platform[0]:
            optimized["priority_platform"] = best_platform[0]
            optimized["optimizations_applied"].append(f"Приоритетная платформа: {best_platform[0]}")
        
        # Логируем оптимизацию
        self._log_optimization(current_strategy, optimized)
        
        return optimized
    
    def _log_optimization(self, before: Dict, after: Dict):
        """Логирование оптимизации"""
        log = []
        if OPTIMIZATION_LOG_FILE.exists():
            try:
                with open(OPTIMIZATION_LOG_FILE, 'r') as f:
                    log = json.load(f)
            except:
                pass
        
        log.append({
            "timestamp": datetime.now().isoformat(),
            "changes": after.get("optimizations_applied", [])
        })
        
        log = log[-100:]
        
        with open(OPTIMIZATION_LOG_FILE, 'w') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
    
    # ═══════════════════════════════════════════════════════════════
    # ПРЕДСКАЗАНИЯ
    # ═══════════════════════════════════════════════════════════════
    
    def predict_ranking_potential(self, keyword: str, domain: str, current_position: Optional[int] = None) -> Dict:
        """
        Предсказание потенциала ранжирования
        На основе исторических данных
        """
        prediction = {
            "keyword": keyword,
            "domain": domain,
            "current_position": current_position,
            "predicted_position": None,
            "confidence": 0,
            "time_to_rank": None,
            "factors": []
        }
        
        # Анализируем похожие случаи
        patterns = self.seo_patterns.get("patterns", [])
        similar_cases = []
        
        for pattern in patterns:
            metrics = pattern.get("metrics", {})
            if metrics.get("avg_position"):
                similar_cases.append({
                    "position": metrics["avg_position"],
                    "success_score": pattern.get("success_score", 0)
                })
        
        if similar_cases:
            # Простая модель предсказания
            avg_success = sum(c["success_score"] for c in similar_cases) / len(similar_cases)
            avg_position = sum(c["position"] for c in similar_cases) / len(similar_cases)
            
            if avg_success > 50:
                prediction["predicted_position"] = round(avg_position * 0.8)
                prediction["confidence"] = min(avg_success, 80)
                prediction["time_to_rank"] = "2-4 недели"
            else:
                prediction["predicted_position"] = round(avg_position * 1.2)
                prediction["confidence"] = min(avg_success, 50)
                prediction["time_to_rank"] = "4-8 недель"
            
            prediction["factors"] = [
                f"На основе {len(similar_cases)} похожих случаев",
                f"Средний показатель успеха: {round(avg_success)}%"
            ]
        else:
            prediction["predicted_position"] = 50
            prediction["confidence"] = 20
            prediction["time_to_rank"] = "Недостаточно данных"
            prediction["factors"] = ["Недостаточно исторических данных для точного предсказания"]
        
        return prediction
    
    def get_learning_stats(self) -> Dict:
        """Получение статистики обучения"""
        return {
            "patterns_learned": len(self.seo_patterns.get("patterns", [])),
            "content_samples": {
                "successful": len(self.content_analysis.get("successful", [])),
                "failed": len(self.content_analysis.get("failed", []))
            },
            "platforms_analyzed": len(self.platform_stats.get("platforms", {})),
            "strategies_optimized": len(self.strategy_scores.get("history", [])),
            "last_learning": self.seo_patterns.get("patterns", [{}])[-1].get("timestamp", "Never") if self.seo_patterns.get("patterns") else "Never"
        }


# Singleton
_learning_engine = None

def get_learning_engine() -> SEOLearningEngine:
    """Получение экземпляра движка обучения"""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = SEOLearningEngine()
    return _learning_engine
