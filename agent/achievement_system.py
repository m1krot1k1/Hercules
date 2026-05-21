"""
Achievement System - система геймификации и достижений.

Предоставляет мотивацию для эффективного использования через
"Achievement Unlocked: 1000 tokens saved!", "First Autonomous Fix"
и визуализацию прогресса в UI.
"""

import json
import threading
import time
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

from hermes_constants import get_hermes_home


class AchievementTier(Enum):
    """Уровни достижений."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


@dataclass
class Achievement:
    """Описание достижения."""
    achievement_id: str
    name: str
    description: str
    emoji: str
    tier: AchievementTier = AchievementTier.BRONZE
    condition: str = ""  # Описание условия получения
    max_progress: Optional[int] = None  # None = одноразовое достижение
    points: int = 10  # Очки за достижение
    hidden: bool = False  # Скрытое достижение (показывается только после получения)
    category: str = "general"  # Категория: general, efficiency, speed, quality
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует достижение в словарь."""
        return {
            "achievement_id": self.achievement_id,
            "name": self.name,
            "description": self.description,
            "emoji": self.emoji,
            "tier": self.tier.value,
            "condition": self.condition,
            "max_progress": self.max_progress,
            "points": self.points,
            "hidden": self.hidden,
            "category": self.category
        }


@dataclass
class UnlockedAchievement:
    """Информация о разблокированном достижении."""
    achievement_id: str
    agent_id: str
    unlocked_at: float = field(default_factory=time.time)
    progress: int = 100  # Для многоэтапных достижений (0-100)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует в словарь."""
        return {
            "achievement_id": self.achievement_id,
            "agent_id": self.agent_id,
            "unlocked_at": self.unlocked_at,
            "formatted_time": datetime.fromtimestamp(self.unlocked_at).isoformat(),
            "progress": self.progress
        }


class AchievementSystem:
    """
    Система достижений для мотивации пользователей.
    
    Отслеживает выполнение различных условий и разблокирует
    достижения с визуализацией прогресса.
    """
    
    def __init__(self):
        """Инициализация системы достижений."""
        self._achievements: Dict[str, Achievement] = {}
        self._unlocked: Dict[str, List[UnlockedAchievement]] = {}  # agent_id -> list
        self._progress: Dict[str, Dict[str, int]] = {}  # agent_id -> {achievement_id: progress}
        self._lock = threading.Lock() if threading else None
        
        # Директория для сохранения
        self.storage_dir = get_hermes_home() / "achievements"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self._init_default_achievements()
        self._load_all()
    
    def _init_default_achievements(self):
        """Инициализирует список достижений по умолчанию."""
        
        # Первые шаги
        self._achievements["first_task"] = Achievement(
            achievement_id="first_task",
            name="First Task",
            description="Первая выполненная задача",
            emoji="🏆",
            tier=AchievementTier.BRONZE,
            condition="Выполнить первую задачу",
            points=10,
            category="milestone"
        )
        
        # Экономия токенов
        self._achievements["token_saver_1"] = Achievement(
            achievement_id="token_saver_1",
            name="Token Saver I",
            description="Сэкономлено 1000 токенов",
            emoji="💰",
            tier=AchievementTier.BRONZE,
            condition="Сэкономить 1000 токенов",
            max_progress=1000,
            points=20,
            category="efficiency"
        )
        
        self._achievements["token_saver_2"] = Achievement(
            achievement_id="token_saver_2",
            name="Token Saver II",
            description="Сэкономлено 5000 токенов",
            emoji="💎",
            tier=AchievementTier.SILVER,
            condition="Сэкономить 5000 токенов",
            max_progress=5000,
            points=50,
            category="efficiency"
        )
        
        self._achievements["token_saver_3"] = Achievement(
            achievement_id="token_saver_3",
            name="Token Saver III",
            description="Сэкономлено 10000 токенов",
            emoji="🏅",
            tier=AchievementTier.GOLD,
            condition="Сэкономить 10000 токенов",
            max_progress=10000,
            points=100,
            category="efficiency"
        )
        
        # Автономное исправление
        self._achievements["autonomous_fix"] = Achievement(
            achievement_id="autonomous_fix",
            name="Autonomous Fix",
            description="Самостоятельное исправление ошибки",
            emoji="🤖",
            tier=AchievementTier.SILVER,
            condition="Исправить ошибку без помощи пользователя",
            points=30,
            category="quality"
        )
        
        # Скорость
        self._achievements["speed_runner_1"] = Achievement(
            achievement_id="speed_runner_1",
            name="Speed Runner I",
            description="Задача выполнена менее чем за 1 минуту",
            emoji="⚡",
            tier=AchievementTier.BRONZE,
            condition="Выполнить задачу быстрее чем за 60 секунд",
            points=25,
            category="speed"
        )
        
        self._achievements["speed_runner_2"] = Achievement(
            achievement_id="speed_runner_2",
            name="Speed Runner II",
            description="Задача выполнена менее чем за 30 секунд",
            emoji="⚡",
            tier=AchievementTier.SILVER,
            condition="Выполнить задачу быстрее чем за 30 секунд",
            points=50,
            category="speed"
        )
        
        # Использование инструментов
        self._achievements["tool_master"] = Achievement(
            achievement_id="tool_master",
            name="Tool Master",
            description="Использовано 10 различных инструментов",
            emoji="🔧",
            tier=AchievementTier.SILVER,
            condition="Использовать 10 различных инструментов",
            max_progress=10,
            points=40,
            category="usage"
        )
        
        # Делегирование
        self._achievements["delegation_pro"] = Achievement(
            achievement_id="delegation_pro",
            name="Delegation Pro",
            description="Делегировано 5 задач субагентам",
            emoji="👥",
            tier=AchievementTier.BRONZE,
            condition="Делегировать 5 задач",
            max_progress=5,
            points=30,
            category="usage"
        )
        
        # Чекпоинты
        self._achievements["checkpoint_creator"] = Achievement(
            achievement_id="checkpoint_creator",
            name="Checkpoint Creator",
            description="Создано 3 контрольные точки",
            emoji="💾",
            tier=AchievementTier.BRONZE,
            condition="Создать 3 чекпоинта",
            max_progress=3,
            points=20,
            category="usage"
        )
        
        # Роевой интеллект
        self._achievements["swarm_participant"] = Achievement(
            achievement_id="swarm_participant",
            name="Swarm Participant",
            description="Участие в роевом взаимодействии",
            emoji="🐝",
            tier=AchievementTier.SILVER,
            condition="Опубликовать 5 сообщений в swarm bus",
            max_progress=5,
            points=35,
            category="collaboration"
        )
        
        # Серийный работник
        self._achievements["marathon_runner"] = Achievement(
            achievement_id="marathon_runner",
            name="Marathon Runner",
            description="Выполнено 50 задач в одной сессии",
            emoji="🏃",
            tier=AchievementTier.GOLD,
            condition="Выполнить 50 задач",
            max_progress=50,
            points=100,
            category="milestone"
        )
    
    def check_achievements(self, agent_id: str, telemetry: Dict[str, Any]) -> List[Achievement]:
        """
        Проверяет условия достижений на основе телеметрии.
        
        Args:
            agent_id: ID агента
            telemetry: Словарь с данными телеметрии:
                - tokens_used: использовано токенов
                - tokens_saved: сэкономлено токенов
                - task_duration: длительность задачи в секундах
                - tools_used: список использованных инструментов
                - tasks_completed: количество выполненных задач
                - autonomous_fixes: количество автономных исправлений
                - checkpoints_created: количество созданных чекпоинтов
                - swarm_messages: количество сообщений в swarm
        
        Returns:
            Список новых разблокированных достижений
        """
        newly_unlocked = []
        
        with self._lock or nullcontext():
            for ach_id, achievement in self._achievements.items():
                # Пропускаем уже разблокированные
                if self._is_unlocked(agent_id, ach_id):
                    continue
                
                # Проверяем условия
                if self._check_single_achievement(agent_id, achievement, telemetry):
                    unlocked = self.unlock_achievement(agent_id, ach_id)
                    if unlocked:
                        newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def _check_single_achievement(self, agent_id: str, achievement: Achievement, 
                                   telemetry: Dict[str, Any]) -> bool:
        """Проверяет одно достижение."""
        
        if agent_id not in self._progress:
            self._progress[agent_id] = {}
        
        progress = self._progress[agent_id]
        
        # First Task
        if achievement.achievement_id == "first_task":
            return telemetry.get("tasks_completed", 0) >= 1
        
        # Token Saver
        elif achievement.achievement_id.startswith("token_saver_"):
            tokens_saved = telemetry.get("tokens_saved", 0)
            max_prog = achievement.max_progress or 1
            progress[achievement.achievement_id] = min(tokens_saved, max_prog)
            return tokens_saved >= max_prog
        
        # Autonomous Fix
        elif achievement.achievement_id == "autonomous_fix":
            return telemetry.get("autonomous_fixes", 0) >= 1
        
        # Speed Runner
        elif achievement.achievement_id.startswith("speed_runner_"):
            duration = telemetry.get("task_duration", float('inf'))
            threshold = 60 if "1" in achievement.achievement_id else 30
            return duration < threshold
        
        # Tool Master
        elif achievement.achievement_id == "tool_master":
            tools_used = set(telemetry.get("tools_used", []))
            progress[achievement.achievement_id] = len(tools_used)
            return len(tools_used) >= 10
        
        # Delegation Pro
        elif achievement.achievement_id == "delegation_pro":
            delegations = telemetry.get("delegations_count", 0)
            progress[achievement.achievement_id] = min(delegations, 5)
            return delegations >= 5
        
        # Checkpoint Creator
        elif achievement.achievement_id == "checkpoint_creator":
            checkpoints = telemetry.get("checkpoints_created", 0)
            progress[achievement.achievement_id] = min(checkpoints, 3)
            return checkpoints >= 3
        
        # Swarm Participant
        elif achievement.achievement_id == "swarm_participant":
            messages = telemetry.get("swarm_messages", 0)
            progress[achievement.achievement_id] = min(messages, 5)
            return messages >= 5
        
        # Marathon Runner
        elif achievement.achievement_id == "marathon_runner":
            tasks = telemetry.get("tasks_completed", 0)
            progress[achievement.achievement_id] = min(tasks, 50)
            return tasks >= 50
        
        return False
    
    def unlock_achievement(self, agent_id: str, achievement_id: str, 
                           progress: int = 100) -> bool:
        """
        Разблокирует достижение для агента.
        
        Args:
            agent_id: ID агента
            achievement_id: ID достижения
            progress: Прогресс (для многоэтапных, 0-100)
        
        Returns:
            True если достижение новое
        """
        if achievement_id not in self._achievements:
            return False
        
        with self._lock or nullcontext():
            if self._is_unlocked(agent_id, achievement_id):
                return False
            
            if agent_id not in self._unlocked:
                self._unlocked[agent_id] = []
            
            unlocked = UnlockedAchievement(
                achievement_id=achievement_id,
                agent_id=agent_id,
                progress=progress
            )
            self._unlocked[agent_id].append(unlocked)
            
            self._save_agent(agent_id)
            return True
    
    def _is_unlocked(self, agent_id: str, achievement_id: str) -> bool:
        """Проверяет, разблокировано ли достижение."""
        if agent_id not in self._unlocked:
            return False
        return any(u.achievement_id == achievement_id for u in self._unlocked[agent_id])
    
    def get_unlocked(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Возвращает список разблокированных достижений агента.
        
        Args:
            agent_id: ID агента
        
        Returns:
            Список словарей с информацией о достижениях
        """
        result = []
        with self._lock or nullcontext():
            if agent_id in self._unlocked:
                for u in self._unlocked[agent_id]:
                    ach = self._achievements.get(u.achievement_id)
                    if ach:
                        result.append({
                            "achievement": ach.to_dict(),
                            "unlocked_at": u.unlocked_at,
                            "formatted_time": datetime.fromtimestamp(u.unlocked_at).isoformat(),
                            "progress": u.progress
                        })
        return result
    
    def get_progress(self, agent_id: str, achievement_id: str) -> int:
        """
        Возвращает прогресс многоэтапного достижения.
        
        Args:
            agent_id: ID агента
            achievement_id: ID достижения
        
        Returns:
            Прогресс (0-100) или 0 если не найдено
        """
        with self._lock or nullcontext():
            if agent_id in self._progress:
                return self._progress[agent_id].get(achievement_id, 0)
        return 0
    
    def get_all_achievements(self) -> List[Dict[str, Any]]:
        """
        Возвращает список всех доступных достижений.
        
        Returns:
            Список словарей с описанием достижений
        """
        return [ach.to_dict() for ach in self._achievements.values()]
    
    def get_agent_points(self, agent_id: str) -> int:
        """
        Возвращает общее количество очков агента.
        
        Args:
            agent_id: ID агента
        
        Returns:
            Сумма очков за разблокированные достижения
        """
        total = 0
        with self._lock or nullcontext():
            if agent_id in self._unlocked:
                for u in self._unlocked[agent_id]:
                    ach = self._achievements.get(u.achievement_id)
                    if ach:
                        total += ach.points
        return total
    
    def _save_agent(self, agent_id: str):
        """Сохраняет достижения агента в файл."""
        if agent_id not in self._unlocked:
            return
        
        filepath = self.storage_dir / f"{agent_id}.json"
        data = {
            "agent_id": agent_id,
            "unlocked": [u.to_dict() for u in self._unlocked[agent_id]],
            "progress": self._progress.get(agent_id, {})
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Ошибка сохранения достижений: {e}")
    
    def _load_all(self):
        """Загружает достижения всех агентов."""
        if not self.storage_dir.exists():
            return
        
        for filepath in self.storage_dir.iterdir():
            if filepath.is_file() and filepath.suffix == '.json':
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    agent_id = data.get("agent_id")
                    if agent_id:
                        # Загружаем разблокированные
                        self._unlocked[agent_id] = [
                            UnlockedAchievement(
                                achievement_id=u["achievement_id"],
                                agent_id=u["agent_id"],
                                unlocked_at=u.get("unlocked_at", time.time()),
                                progress=u.get("progress", 100)
                            )
                            for u in data.get("unlocked", [])
                        ]
                        # Загружаем прогресс
                        self._progress[agent_id] = data.get("progress", {})
                except (json.JSONDecodeError, IOError):
                    continue


# Глобальный экземпляр
_achievement_system: Optional[AchievementSystem] = None
_as_lock = threading.Lock() if threading else None


def get_achievement_system() -> AchievementSystem:
    """
    Получает глобальный экземпляр системы достижений.
    
    Returns:
        Экземпляр AchievementSystem
    """
    global _achievement_system
    with _as_lock or nullcontext():
        if _achievement_system is None:
            _achievement_system = AchievementSystem()
        return _achievement_system


def check_achievements(agent_id: str, telemetry: Dict[str, Any]) -> List:
    """
    Удобная функция для проверки достижений.
    
    Args:
        agent_id: ID агента
        telemetry: Данные телеметрии
    
    Returns:
        Список новых достижений
    """
    system = get_achievement_system()
    return system.check_achievements(agent_id, telemetry)


def unlock_achievement(agent_id: str, achievement_id: str) -> bool:
    """
    Удобная функция для разблокировки достижения.
    
    Args:
        agent_id: ID агента
        achievement_id: ID достижения
    
    Returns:
        True если достижение новое
    """
    system = get_achievement_system()
    return system.unlock_achievement(agent_id, achievement_id)


def get_unlocked_achievements(agent_id: str) -> List[Dict[str, Any]]:
    """
    Удобная функция для получения разблокированных достижений.
    
    Args:
        agent_id: ID агента
    
    Returns:
        Список достижений
    """
    system = get_achievement_system()
    return system.get_unlocked(agent_id)
