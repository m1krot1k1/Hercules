"""
Swarm Bus - система роевого интеллекта для P2P общения агентов.

Позволяет агентам общаться друг с другом напрямую (peer-to-peer),
а не только иерархически. Subagents могут делиться промежуточными
результатами с другими subagents через pub/sub систему.
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum

from hermes_constants import get_hermes_home


class MessagePriority(Enum):
    """Приоритет сообщения в роевой системе."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SwarmMessage:
    """Сообщение в роевой системе."""
    topic: str
    message: Any
    sender_id: str
    timestamp: float = field(default_factory=time.time)
    priority: MessagePriority = MessagePriority.NORMAL
    message_id: str = field(default_factory=lambda: f"msg_{int(time.time() * 1000)}")
    recipients: Optional[List[str]] = None  # None = всем подписчикам темы
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует сообщение в словарь для сериализации."""
        return {
            "message_id": self.message_id,
            "topic": self.topic,
            "message": self.message,
            "sender_id": self.sender_id,
            "timestamp": self.timestamp,
            "formatted_time": datetime.fromtimestamp(self.timestamp).isoformat(),
            "priority": self.priority.value,
            "recipients": self.recipients
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SwarmMessage':
        """Создает сообщение из словаря."""
        return cls(
            topic=data["topic"],
            message=data["message"],
            sender_id=data["sender_id"],
            timestamp=data.get("timestamp", time.time()),
            priority=MessagePriority(data.get("priority", "normal")),
            message_id=data.get("message_id", f"msg_{int(time.time() * 1000)}"),
            recipients=data.get("recipients")
        )


class SwarmBus:
    """
    Шина сообщений для роевого интеллекта агентов.
    
    Реализует паттерн Publisher-Subscriber для асинхронного
    обмена сообщениями между агентами.
    """
    
    def __init__(self, bus_id: str = "default"):
        """
        Инициализация шины сообщений.
        
        Args:
            bus_id: Уникальный идентификатор шины (для множественных роев)
        """
        self.bus_id = bus_id
        self._subscribers: Dict[str, Dict[str, Callable]] = {}  # topic -> {agent_id: callback}
        self._message_history: Dict[str, List[SwarmMessage]] = {}  # topic -> messages
        self._agent_topics: Dict[str, Set[str]] = {}  # agent_id -> set of topics
        self._lock = threading.RLock()
        
        # Директория для персистентности (опционально)
        self.storage_dir = get_hermes_home() / "swarm" / bus_id
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._max_history_per_topic = 100
    
    def publish(self, topic: str, message: Any, sender_id: str, 
                priority: MessagePriority = MessagePriority.NORMAL,
                recipients: Optional[List[str]] = None) -> str:
        """
        Публикует сообщение в указанную тему.
        
        Args:
            topic: Тема сообщения (например, "code/bugs", "test/results")
            message: Содержимое сообщения (должно быть сериализуемым)
            sender_id: ID агента-отправителя
            priority: Приоритет сообщения
            recipients: Список ID конкретных получателей (None = всем подписчикам)
        
        Returns:
            ID опубликованного сообщения
        """
        swarm_message = SwarmMessage(
            topic=topic,
            message=message,
            sender_id=sender_id,
            priority=priority,
            recipients=recipients
        )
        
        with self._lock:
            # Сохраняем в историю
            if topic not in self._message_history:
                self._message_history[topic] = []
            self._message_history[topic].append(swarm_message)
            
            # Ограничиваем историю
            if len(self._message_history[topic]) > self._max_history_per_topic:
                self._message_history[topic] = self._message_history[topic][-self._max_history_per_topic:]
            
            # Сохраняем в файл для персистентности
            self._persist_message(swarm_message)
            
            # Уведомляем подписчиков
            if topic in self._subscribers:
                for agent_id, callback in self._subscribers[topic].items():
                    # Если указаны конкретные получатели, проверяем
                    if recipients is None or agent_id in recipients:
                        try:
                            callback(swarm_message)
                        except Exception as e:
                            print(f"Ошибка в callback подписчика {agent_id}: {e}")
        
        return swarm_message.message_id
    
    def subscribe(self, topic: str, agent_id: str, callback: Callable[[SwarmMessage], None]) -> bool:
        """
        Подписывает агента на тему.
        
        Args:
            topic: Тема для подписки
            agent_id: ID агента-подписчика
            callback: Функция обратного вызова при получении сообщения
        
        Returns:
            True если подписка успешна
        """
        with self._lock:
            if topic not in self._subscribers:
                self._subscribers[topic] = {}
            self._subscribers[topic][agent_id] = callback
            
            # Отслеживаем темы агента
            if agent_id not in self._agent_topics:
                self._agent_topics[agent_id] = set()
            self._agent_topics[agent_id].add(topic)
        
        return True
    
    def unsubscribe(self, topic: str, agent_id: str) -> bool:
        """
        Отписывает агента от темы.
        
        Args:
            topic: Тема для отписки
            agent_id: ID агента
        
        Returns:
            True если отписка успешна
        """
        with self._lock:
            if topic in self._subscribers and agent_id in self._subscribers[topic]:
                del self._subscribers[topic][agent_id]
                
                # Очищаем пустые темы
                if not self._subscribers[topic]:
                    del self._subscribers[topic]
                
                # Убираем из отслеживания
                if agent_id in self._agent_topics:
                    self._agent_topics[agent_id].discard(topic)
                
                return True
        return False
    
    def unsubscribe_all(self, agent_id: str) -> int:
        """
        Отписывает агента от всех тем.
        
        Args:
            agent_id: ID агента
        
        Returns:
            Количество отписок
        """
        count = 0
        with self._lock:
            if agent_id in self._agent_topics:
                topics = list(self._agent_topics[agent_id])
                for topic in topics:
                    if self.unsubscribe(topic, agent_id):
                        count += 1
                del self._agent_topics[agent_id]
        return count
    
    def get_messages(self, agent_id: str, topic: Optional[str] = None, 
                     since_timestamp: Optional[float] = None) -> List[SwarmMessage]:
        """
        Получает сообщения для агента.
        
        Args:
            agent_id: ID агента-получателя
            topic: Конкретная тема (None = все доступные темы)
            since_timestamp: Получить сообщения после указанного времени
        
        Returns:
            Список сообщений
        """
        messages = []
        
        with self._lock:
            if topic:
                # Конкретная тема
                if topic in self._message_history:
                    for msg in self._message_history[topic]:
                        if self._is_message_for_agent(msg, agent_id):
                            if since_timestamp is None or msg.timestamp > since_timestamp:
                                messages.append(msg)
            else:
                # Все темы, на которые подписан агент
                if agent_id in self._agent_topics:
                    for t in self._agent_topics[agent_id]:
                        if t in self._message_history:
                            for msg in self._message_history[t]:
                                if since_timestamp is None or msg.timestamp > since_timestamp:
                                    messages.append(msg)
        
        # Сортируем по времени
        messages.sort(key=lambda m: m.timestamp)
        return messages
    
    def _is_message_for_agent(self, msg: SwarmMessage, agent_id: str) -> bool:
        """Проверяет, предназначено ли сообщение для агента."""
        if msg.recipients is None:
            return True  # Широковещательное сообщение
        return agent_id in msg.recipients
    
    def _persist_message(self, message: SwarmMessage):
        """Сохраняет сообщение в файл для персистентности."""
        try:
            topic_file = self.storage_dir / f"{message.topic.replace('/', '_')}.jsonl"
            with open(topic_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(message.to_dict(), ensure_ascii=False) + '\n')
        except IOError as e:
            print(f"Ошибка сохранения сообщения: {e}")
    
    def get_topic_subscribers(self, topic: str) -> List[str]:
        """
        Возвращает список подписчиков темы.
        
        Args:
            topic: Тема
        
        Returns:
            Список ID агентов-подписчиков
        """
        with self._lock:
            if topic in self._subscribers:
                return list(self._subscribers[topic].keys())
        return []
    
    def get_agent_topics(self, agent_id: str) -> List[str]:
        """
        Возвращает список тем, на которые подписан агент.
        
        Args:
            agent_id: ID агента
        
        Returns:
            Список тем
        """
        with self._lock:
            if agent_id in self._agent_topics:
                return list(self._agent_topics[agent_id])
        return []
    
    def clear_history(self, topic: Optional[str] = None):
        """
        Очищает историю сообщений.
        
        Args:
            topic: Конкретная тема (None = все темы)
        """
        with self._lock:
            if topic:
                if topic in self._message_history:
                    self._message_history[topic] = []
            else:
                self._message_history.clear()


# Глобальный экземпляр шины для использования в системе
_global_bus: Optional[SwarmBus] = None
_global_bus_lock = threading.Lock()


def get_swarm_bus(bus_id: str = "default") -> SwarmBus:
    """
    Получает глобальный экземпляр шины сообщений.
    
    Args:
        bus_id: ID шины
    
    Returns:
        Экземпляр SwarmBus
    """
    global _global_bus
    with _global_bus_lock:
        if _global_bus is None or _global_bus.bus_id != bus_id:
            _global_bus = SwarmBus(bus_id)
        return _global_bus


def publish(topic: str, message: Any, sender_id: str, 
            priority: MessagePriority = MessagePriority.NORMAL) -> str:
    """
    Удобная функция для публикации сообщения.
    
    Args:
        topic: Тема сообщения
        message: Содержимое
        sender_id: ID отправителя
        priority: Приоритет
    
    Returns:
        ID сообщения
    """
    bus = get_swarm_bus()
    return bus.publish(topic, message, sender_id, priority)


def subscribe(topic: str, agent_id: str, callback: Callable[[SwarmMessage], None]) -> bool:
    """
    Удобная функция для подписки на тему.
    
    Args:
        topic: Тема
        agent_id: ID агента
        callback: Функция обратного вызова
    
    Returns:
        True если успешно
    """
    bus = get_swarm_bus()
    return bus.subscribe(topic, agent_id, callback)


def get_messages(agent_id: str, topic: Optional[str] = None) -> List[SwarmMessage]:
    """
    Удобная функция для получения сообщений.
    
    Args:
        agent_id: ID агента
        topic: Тема (опционально)
    
    Returns:
        Список сообщений
    """
    bus = get_swarm_bus()
    return bus.get_messages(agent_id, topic)
