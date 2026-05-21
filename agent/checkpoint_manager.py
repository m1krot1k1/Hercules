"""
Agent Checkpoint Manager - система контрольных точек для сохранения состояния агента.

Позволяет сохранять состояние агента в процессе работы и восстанавливаться
с последней точки при сбое или таймауте, вместо начала работы с нуля.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from hermes_constants import get_hermes_home


class AgentCheckpoint:
    """
    Класс для управления контрольными точками агента.
    
    Сохраняет состояние агента в JSON-файлы в директории ~/.hermes/checkpoints/
    и обеспечивает восстановление состояния при перезапуске.
    """
    
    def __init__(self, agent_id: str):
        """
        Инициализация менеджера контрольных точек.
        
        Args:
            agent_id: Уникальный идентификатор агента
        """
        self.agent_id = agent_id
        self.checkpoints_dir = get_hermes_home() / "checkpoints"
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
    
    def save_checkpoint(self, state_dict: Dict[str, Any]) -> str:
        """
        Сохраняет состояние агента в контрольную точку.
        
        Args:
            state_dict: Словарь с состоянием агента для сохранения.
                      Должен содержать сериализуемые данные.
        
        Returns:
            Путь к созданному файлу контрольной точки
        
        Raises:
            ValueError: Если state_dict пустой или содержит несериализуемые данные
        """
        if not state_dict:
            raise ValueError("state_dict не может быть пустым")
        
        timestamp = int(time.time())
        formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S")
        filename = f"{self.agent_id}_{formatted_time}_{timestamp}.json"
        filepath = self.checkpoints_dir / filename
        
        # Добавляем метаданные
        checkpoint_data = {
            "agent_id": self.agent_id,
            "timestamp": timestamp,
            "formatted_time": formatted_time,
            "version": "1.0",
            "state": state_dict
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False, default=str)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Ошибка сериализации состояния: {e}")
        
        return str(filepath)
    
    def load_checkpoint(self, checkpoint_file: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Загружает контрольную точку.
        
        Args:
            checkpoint_file: Путь к файлу контрольной точки.
                           Если None, загружается последняя доступная точка.
        
        Returns:
            Словарь с состоянием агента или None, если точки не найдены
        """
        if checkpoint_file:
            filepath = Path(checkpoint_file)
        else:
            # Находим последнюю контрольную точку
            checkpoints = self.list_checkpoints()
            if not checkpoints:
                return None
            filepath = Path(checkpoints[0]["filepath"])
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            return checkpoint_data.get("state", {})
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки контрольной точки: {e}")
            return None
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        Возвращает список доступных контрольных точек для данного агента.
        
        Returns:
            Список словарей с информацией о контрольных точках,
            отсортированный по времени (новые сначала)
        """
        checkpoints = []
        prefix = f"{self.agent_id}_"
        
        if not self.checkpoints_dir.exists():
            return checkpoints
        
        for filepath in self.checkpoints_dir.iterdir():
            if filepath.is_file() and filepath.name.startswith(prefix) and filepath.suffix == '.json':
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    checkpoints.append({
                        "filepath": str(filepath),
                        "filename": filepath.name,
                        "timestamp": data.get("timestamp", 0),
                        "formatted_time": data.get("formatted_time", "unknown"),
                        "agent_id": data.get("agent_id", self.agent_id)
                    })
                except (json.JSONDecodeError, IOError):
                    continue
        
        # Сортируем по timestamp (новые сначала)
        checkpoints.sort(key=lambda x: x["timestamp"], reverse=True)
        return checkpoints
    
    def delete_checkpoint(self, checkpoint_file: str) -> bool:
        """
        Удаляет указанную контрольную точку.
        
        Args:
            checkpoint_file: Путь к файлу контрольной точки
        
        Returns:
            True если удаление успешно, False в противном случае
        """
        filepath = Path(checkpoint_file)
        if filepath.exists() and filepath.is_file():
            try:
                filepath.unlink()
                return True
            except IOError:
                return False
        return False
    
    def cleanup_old_checkpoints(self, keep_last: int = 5) -> int:
        """
        Удаляет старые контрольные точки, оставляя только последние N.
        
        Args:
            keep_last: Количество последних точек для сохранения
        
        Returns:
            Количество удаленных контрольных точек
        """
        checkpoints = self.list_checkpoints()
        if len(checkpoints) <= keep_last:
            return 0
        
        to_delete = checkpoints[keep_last:]
        deleted = 0
        for cp in to_delete:
            if self.delete_checkpoint(cp["filepath"]):
                deleted += 1
        
        return deleted


def save_checkpoint(agent_id: str, state_dict: Dict[str, Any]) -> str:
    """
    Удобная функция для сохранения контрольной точки.
    
    Args:
        agent_id: Уникальный идентификатор агента
        state_dict: Словарь с состоянием агента
    
    Returns:
        Путь к созданному файлу контрольной точки
    """
    checkpoint = AgentCheckpoint(agent_id)
    return checkpoint.save_checkpoint(state_dict)


def load_checkpoint(agent_id: str, checkpoint_file: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Удобная функция для загрузки контрольной точки.
    
    Args:
        agent_id: Уникальный идентификатор агента
        checkpoint_file: Путь к файлу контрольной точки (опционально)
    
    Returns:
        Словарь с состоянием агента или None
    """
    checkpoint = AgentCheckpoint(agent_id)
    return checkpoint.load_checkpoint(checkpoint_file)


def list_checkpoints(agent_id: str) -> List[Dict[str, Any]]:
    """
    Удобная функция для получения списка контрольных точек.
    
    Args:
        agent_id: Уникальный идентификатор агента
    
    Returns:
        Список контрольных точек
    """
    checkpoint = AgentCheckpoint(agent_id)
    return checkpoint.list_checkpoints()
