"""
Task Dependency Graph - граф зависимостей задач.

Позволяет визуализировать в UI какие задачи блокируют другие,
а также автоматически перезапускать зависимые задачи при ошибке.
"""

import json
import threading
import time
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from hermes_constants import get_hermes_home


class TaskStatus(Enum):
    """Статус задачи в графе зависимостей."""
    PENDING = "pending"       # Ожидает выполнения
    READY = "ready"           # Готова к выполнению (зависимости выполнены)
    RUNNING = "running"       # Выполняется
    COMPLETED = "completed"   # Выполнена успешно
    FAILED = "failed"         # Ошибка выполнения
    BLOCKED = "blocked"       # Заблокирована (зависимости не выполнены)
    SKIPPED = "skipped"       # Пропущена


@dataclass
class TaskNode:
    """Узел графа зависимостей - представляет одну задачу."""
    task_id: str
    name: str = ""
    description: str = ""
    depends_on: List[str] = field(default_factory=list)  # ID задач, от которых зависит
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует узел в словарь для сериализации."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "created_at": self.created_at,
            "formatted_created": datetime.fromtimestamp(self.created_at).isoformat(),
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskNode':
        """Создает узел из словаря."""
        return cls(
            task_id=data["task_id"],
            name=data.get("name", ""),
            description=data.get("description", ""),
            depends_on=data.get("depends_on", []),
            status=TaskStatus(data.get("status", "pending")),
            created_at=data.get("created_at", time.time()),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            error_message=data.get("error_message"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            metadata=data.get("metadata", {})
        )


class TaskDependencyGraph:
    """
    Граф зависимостей задач.
    
    Позволяет управлять задачами с учетом их взаимозависимостей,
    визуализировать блокировки и автоматически перезапускать
    зависимые задачи при ошибках.
    """
    
    def __init__(self, graph_id: str = "default"):
        """
        Инициализация графа зависимостей.
        
        Args:
            graph_id: Уникальный идентификатор графа
        """
        self.graph_id = graph_id
        self._tasks: Dict[str, TaskNode] = {}
        self._reverse_deps: Dict[str, Set[str]] = {}  # task_id -> set of tasks that depend on it
        self._lock = threading.Lock() if threading else None
        
        # Директория для сохранения состояния
        self.storage_dir = get_hermes_home() / "dependency_graphs"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._storage_file = self.storage_dir / f"{graph_id}.json"
        
        # Загружаем сохраненное состояние
        self._load()
    
    def add_task(self, task_id: str, depends_on: List[str] = None, 
                 name: str = "", description: str = "", **metadata) -> TaskNode:
        """
        Добавляет задачу в граф.
        
        Args:
            task_id: Уникальный ID задачи
            depends_on: Список ID задач, от которых зависит данная
            name: Человекочитаемое имя задачи
            description: Описание задачи
            **metadata: Дополнительные метаданные
        
        Returns:
            Созданный узел задачи
        
        Raises:
            ValueError: Если задача с таким ID уже существует
        """
        with self._lock or nullcontext():
            if task_id in self._tasks:
                raise ValueError(f"Задача с ID {task_id} уже существует")
            
            depends_on = depends_on or []
            
            # Проверяем циклические зависимости
            if self._would_create_cycle(task_id, depends_on):
                raise ValueError(f"Добавление задачи {task_id} создаст циклическую зависимость")
            
            task = TaskNode(
                task_id=task_id,
                name=name or task_id,
                description=description,
                depends_on=depends_on,
                metadata=metadata
            )
            
            # Определяем начальный статус
            if not depends_on:
                task.status = TaskStatus.READY
            else:
                # Проверяем, выполнены ли все зависимости
                all_completed = all(
                    self._tasks.get(dep, TaskNode(dep)).status == TaskStatus.COMPLETED
                    for dep in depends_on
                )
                task.status = TaskStatus.READY if all_completed else TaskStatus.BLOCKED
            
            self._tasks[task_id] = task
            
            # Обновляем обратные зависимости
            for dep_id in depends_on:
                if dep_id not in self._reverse_deps:
                    self._reverse_deps[dep_id] = set()
                self._reverse_deps[dep_id].add(task_id)
            
            self._save()
            return task
    
    def _would_create_cycle(self, task_id: str, depends_on: List[str]) -> bool:
        """Проверяет, создаст ли добавление задачи циклическую зависимость."""
        # Временно добавляем задачу для проверки
        visited = set()
        
        def has_cycle(node_id):
            if node_id in visited:
                return True
            visited.add(node_id)
            
            # Получаем зависимости
            if node_id == task_id:
                deps = set(depends_on)
            else:
                deps = set(self._tasks[node_id].depends_on) if node_id in self._tasks else set()
            
            for dep in deps:
                if has_cycle(dep):
                    return True
            
            visited.remove(node_id)
            return False
        
        return has_cycle(task_id)
    
    def get_blocked_tasks(self, task_id: str) -> List[str]:
        """
        Возвращает список задач, заблокированных указанной задачей.
        
        Args:
            task_id: ID задачи
        
        Returns:
            Список ID заблокированных задач
        """
        with self._lock or nullcontext():
            if task_id in self._reverse_deps:
                return list(self._reverse_deps[task_id])
        return []
    
    def get_ready_tasks(self) -> List[str]:
        """
        Возвращает список задач, готовых к выполнению.
        
        Returns:
            Список ID задач со статусом READY
        """
        ready = []
        with self._lock or nullcontext():
            for task_id, task in self._tasks.items():
                if task.status == TaskStatus.READY:
                    ready.append(task_id)
        return ready
    
    def get_dependent_tasks(self, task_id: str) -> List[str]:
        """
        Возвращает список задач, от которых зависит указанная.
        
        Args:
            task_id: ID задачи
        
        Returns:
            Список ID задач, от которых зависит данная
        """
        with self._lock or nullcontext():
            if task_id in self._tasks:
                return list(self._tasks[task_id].depends_on)
        return []
    
    def mark_running(self, task_id: str) -> bool:
        """
        Отмечает задачу как выполняющуюся.
        
        Args:
            task_id: ID задачи
        
        Returns:
            True если статус успешно изменен
        """
        with self._lock or nullcontext():
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            if task.status not in (TaskStatus.READY, TaskStatus.PENDING):
                return False
            
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            self._save()
            return True
    
    def mark_completed(self, task_id: str) -> bool:
        """
        Отмечает задачу как выполненную.
        Автоматически обновляет статус зависимых задач.
        
        Args:
            task_id: ID задачи
        
        Returns:
            True если статус успешно изменен
        """
        with self._lock or nullcontext():
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            # Обновляем статус зависимых задач
            self._update_dependent_tasks(task_id)
            
            self._save()
            return True
    
    def mark_failed(self, task_id: str, error_message: str = "") -> bool:
        """
        Отмечает задачу как невыполненную.
        Автоматически блокирует зависимые задачи.
        
        Args:
            task_id: ID задачи
            error_message: Сообщение об ошибке
        
        Returns:
            True если статус успешно изменен
        """
        with self._lock or nullcontext():
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            task.status = TaskStatus.FAILED
            task.error_message = error_message
            task.completed_at = time.time()
            
            # Блокируем зависимые задачи
            self._block_dependent_tasks(task_id)
            
            self._save()
            return True
    
    def retry_task(self, task_id: str) -> bool:
        """
        Повторяет выполнение задачи после ошибки.
        
        Args:
            task_id: ID задачи
        
        Returns:
            True если задача поставлена в очередь на повтор
        """
        with self._lock or nullcontext():
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            if task.status != TaskStatus.FAILED:
                return False
            
            if task.retry_count >= task.max_retries:
                return False  # Превышено количество попыток
            
            task.retry_count += 1
            task.status = TaskStatus.READY
            task.error_message = None
            task.started_at = None
            task.completed_at = None
            
            self._save()
            return True
    
    def _update_dependent_tasks(self, completed_task_id: str):
        """Обновляет статус задач, зависящих от выполненной."""
        if completed_task_id not in self._reverse_deps:
            return
        
        for dependent_id in self._reverse_deps[completed_task_id]:
            if dependent_id in self._tasks:
                dependent = self._tasks[dependent_id]
                if dependent.status == TaskStatus.BLOCKED:
                    # Проверяем, все ли зависимости выполнены
                    all_completed = all(
                        self._tasks.get(dep, TaskNode(dep)).status == TaskStatus.COMPLETED
                        for dep in dependent.depends_on
                    )
                    if all_completed:
                        dependent.status = TaskStatus.READY
    
    def _block_dependent_tasks(self, failed_task_id: str):
        """Блокирует задачи, зависящие от упавшей."""
        if failed_task_id not in self._reverse_deps:
            return
        
        for dependent_id in self._reverse_deps[failed_task_id]:
            if dependent_id in self._tasks:
                self._tasks[dependent_id].status = TaskStatus.BLOCKED
    
    def get_task(self, task_id: str) -> Optional[TaskNode]:
        """Возвращает узел задачи по ID."""
        return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> List[TaskNode]:
        """Возвращает список всех задач."""
        return list(self._tasks.values())
    
    def get_graph_visualization_data(self) -> Dict[str, Any]:
        """
        Возвращает данные для визуализации графа.
        
        Returns:
            Словарь с узлами и ребрами для визуализации
        """
        nodes = []
        edges = []
        
        for task in self._tasks.values():
            nodes.append({
                "id": task.task_id,
                "label": task.name or task.task_id,
                "status": task.status.value,
                "group": task.status.value
            })
            
            for dep_id in task.depends_on:
                edges.append({
                    "from": dep_id,
                    "to": task.task_id,
                    "arrows": "to"
                })
        
        return {"nodes": nodes, "edges": edges}
    
    def _save(self):
        """Сохраняет состояние графа в файл."""
        try:
            data = {
                "graph_id": self.graph_id,
                "tasks": {tid: task.to_dict() for tid, task in self._tasks.items()},
                "reverse_deps": {k: list(v) for k, v in self._reverse_deps.items()}
            }
            with open(self._storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except IOError as e:
            print(f"Ошибка сохранения графа: {e}")
    
    def _load(self):
        """Загружает состояние графа из файла."""
        if not self._storage_file.exists():
            return
        
        try:
            with open(self._storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.graph_id = data.get("graph_id", self.graph_id)
            
            # Загружаем задачи
            for tid, task_data in data.get("tasks", {}).items():
                self._tasks[tid] = TaskNode.from_dict(task_data)
            
            # Загружаем обратные зависимости
            for tid, deps in data.get("reverse_deps", {}).items():
                self._reverse_deps[tid] = set(deps)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки графа: {e}")


# Глобальный реестр графов
_graphs: Dict[str, TaskDependencyGraph] = {}
_graph_lock = threading.Lock() if threading else None


def get_dependency_graph(graph_id: str = "default") -> TaskDependencyGraph:
    """
    Получает или создает граф зависимостей.
    
    Args:
        graph_id: ID графа
    
    Returns:
        Экземпляр TaskDependencyGraph
    """
    with _graph_lock or nullcontext():
        if graph_id not in _graphs:
            _graphs[graph_id] = TaskDependencyGraph(graph_id)
        return _graphs[graph_id]
