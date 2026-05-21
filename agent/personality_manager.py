"""
Personality Manager - система личностей агентов.

Позволяет задавать разные стили работы агентов:
- "Concise" (минимум токенов)
- "Thorough" (максимум качества)
- "Creative" (нестандартные решения)
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field


class PersonalityType(Enum):
    """Типы личностей агентов."""
    CONCISE = "concise"
    THOROUGH = "thorough"
    CREATIVE = "creative"
    BALANCED = "balanced"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"


@dataclass
class Personality:
    """Описание личности агента."""
    name: str
    display_name: str
    description: str
    system_prompt_modifier: str
    examples: List[str] = field(default_factory=list)
    temperature_adjustment: float = 0.0  # Корректировка temperature
    max_tokens_multiplier: float = 1.0    # Множитель max_tokens
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует личность в словарь."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "system_prompt_modifier": self.system_prompt_modifier,
            "examples": self.examples,
            "temperature_adjustment": self.temperature_adjustment,
            "max_tokens_multiplier": self.max_tokens_multiplier,
            "tags": self.tags
        }


class PersonalityManager:
    """
    Менеджер личностей агентов.
    
    Управляет предустановленными личностями и предоставляет
    методы для получения модификаторов system prompt.
    """
    
    def __init__(self):
        """Инициализация менеджера личностей с предустановками."""
        self._personalities: Dict[str, Personality] = {}
        self._init_default_personalities()
    
    def _init_default_personalities(self):
        """Инициализирует предустановленные личности."""
        
        # Concise - минимум токенов
        self._personalities[PersonalityType.CONCISE.value] = Personality(
            name=PersonalityType.CONCISE.value,
            display_name="Concise",
            description="Краткий стиль общения, минимум токенов",
            system_prompt_modifier=(
                "You are a concise assistant. Follow these rules:\n"
                "- Be extremely brief and to the point\n"
                "- Use bullet points for lists\n"
                "- Skip unnecessary explanations\n"
                "- Provide only essential information\n"
                "- Avoid verbose introductions or conclusions"
            ),
            examples=[
                "❌ Don't: 'I think the best approach would be to consider using...'",
                "✓ Do: 'Use X. Reasons: 1, 2, 3.'"
            ],
            temperature_adjustment=-0.2,
            max_tokens_multiplier=0.6,
            tags=["brief", "efficient", "direct"]
        )
        
        # Thorough - максимум качества
        self._personalities[PersonalityType.THOROUGH.value] = Personality(
            name=PersonalityType.THOROUGH.value,
            display_name="Thorough",
            description="Детальный анализ, максимум качества",
            system_prompt_modifier=(
                "You are a thorough and detailed assistant. Follow these rules:\n"
                "- Provide comprehensive explanations\n"
                "- Consider all edge cases\n"
                "- Verify solutions thoroughly\n"
                "- Include examples and counterexamples\n"
                "- Explain your reasoning step by step\n"
                "- Double-check your work before concluding"
            ),
            examples=[
                "✓ Do: 'Let me analyze this step by step. First, consider X. "
                "This could lead to Y, but we must also account for Z...'"
            ],
            temperature_adjustment=-0.1,
            max_tokens_multiplier=1.5,
            tags=["detailed", "comprehensive", "careful"]
        )
        
        # Creative - нестандартные решения
        self._personalities[PersonalityType.CREATIVE.value] = Personality(
            name=PersonalityType.CREATIVE.value,
            display_name="Creative",
            description="Нестандартные подходы и креативные решения",
            system_prompt_modifier=(
                "You are a creative assistant. Follow these rules:\n"
                "- Think outside the box\n"
                "- Consider unconventional approaches\n"
                "- Suggest innovative solutions\n"
                "- Challenge assumptions\n"
                "- Combine ideas from different domains\n"
                "- Don't be afraid to propose radical solutions"
            ),
            examples=[
                "✓ Do: 'While the standard approach is X, we could also consider Y. "
                "What if we combined Z with W? This unconventional approach might...'"
            ],
            temperature_adjustment=0.3,
            max_tokens_multiplier=1.2,
            tags=["innovative", "unconventional", "imaginative"]
        )
        
        # Balanced - сбалансированный стиль
        self._personalities[PersonalityType.BALANCED.value] = Personality(
            name=PersonalityType.BALANCED.value,
            display_name="Balanced",
            description="Сбалансированный стиль общения",
            system_prompt_modifier=(
                "You are a balanced assistant. Follow these rules:\n"
                "- Provide clear and helpful responses\n"
                "- Include necessary details without over-explaining\n"
                "- Balance brevity with completeness\n"
                "- Adapt your style to the task at hand\n"
                "- Be practical and solution-oriented"
            ),
            examples=[
                "✓ Do: 'Here's the solution: [approach]. Key points: 1, 2, 3. "
                "Let me know if you need more details on any part.'"
            ],
            temperature_adjustment=0.0,
            max_tokens_multiplier=1.0,
            tags=["balanced", "adaptive", "practical"]
        )
        
        # Technical - технический фокус
        self._personalities[PersonalityType.TECHNICAL.value] = Personality(
            name=PersonalityType.TECHNICAL.value,
            display_name="Technical",
            description="Технический стиль с акцентом на реализацию",
            system_prompt_modifier=(
                "You are a technical assistant. Follow these rules:\n"
                "- Focus on implementation details\n"
                "- Use precise technical terminology\n"
                "- Include code examples and snippets\n"
                "- Reference documentation and standards\n"
                "- Consider performance and security implications\n"
                "- Provide concrete, actionable steps"
            ),
            examples=[
                "✓ Do: 'Implementation approach: Use X API with Y pattern. "
                "Code example: [snippet]. Performance impact: Z.'"
            ],
            temperature_adjustment=-0.1,
            max_tokens_multiplier=1.3,
            tags=["technical", "precise", "implementation-focused"]
        )
        
        # Friendly - дружелюбный стиль
        self._personalities[PersonalityType.FRIENDLY.value] = Personality(
            name=PersonalityType.FRIENDLY.value,
            display_name="Friendly",
            description="Дружелюбный и доступный стиль общения",
            system_prompt_modifier=(
                "You are a friendly and approachable assistant. Follow these rules:\n"
                "- Use warm and welcoming tone\n"
                "- Explain concepts in simple terms\n"
                "- Encourage and motivate the user\n"
                "- Use examples that are easy to relate to\n"
                "- Be patient and understanding\n"
                "- Celebrate progress and achievements"
            ),
            examples=[
                "✓ Do: 'Great question! Let me help you with that. "
                "Think of it like X - it's similar to Y. You're doing awesome work!'"
            ],
            temperature_adjustment=0.1,
            max_tokens_multiplier=1.1,
            tags=["friendly", "approachable", "encouraging"]
        )
    
    def get_personality(self, personality_name: str) -> Optional[Personality]:
        """
        Получает личность по имени.
        
        Args:
            personality_name: Имя личности (concise, thorough, creative, etc.)
        
        Returns:
            Объект Personality или None, если не найдена
        """
        return self._personalities.get(personality_name.lower())
    
    def get_personality_prompt(self, personality_name: str) -> str:
        """
        Возвращает модификатор system prompt для указанной личности.
        
        Args:
            personality_name: Имя личности
        
        Returns:
            Строка с дополнительными инструкциями для system prompt.
            Пустая строка, если личность не найдена.
        """
        personality = self.get_personality(personality_name)
        if personality:
            return personality.system_prompt_modifier
        return ""
    
    def get_temperature_adjustment(self, personality_name: str) -> float:
        """
        Возвращает корректировку temperature для личности.
        
        Args:
            personality_name: Имя личности
        
        Returns:
            Значение корректировки (может быть отрицательным)
        """
        personality = self.get_personality(personality_name)
        if personality:
            return personality.temperature_adjustment
        return 0.0
    
    def get_max_tokens_multiplier(self, personality_name: str) -> float:
        """
        Возвращает множитель max_tokens для личности.
        
        Args:
            personality_name: Имя личности
        
        Returns:
            Множитель (1.0 = без изменений)
        """
        personality = self.get_personality(personality_name)
        if personality:
            return personality.max_tokens_multiplier
        return 1.0
    
    def list_personalities(self) -> List[Dict[str, Any]]:
        """
        Возвращает список всех доступных личностей.
        
        Returns:
            Список словарей с информацией о личностях
        """
        return [
            {
                "name": p.name,
                "display_name": p.display_name,
                "description": p.description,
                "tags": p.tags
            }
            for p in self._personalities.values()
        ]
    
    def register_personality(self, personality: Personality) -> bool:
        """
        Регистрирует новую личность.
        
        Args:
            personality: Объект Personality
        
        Returns:
            True если регистрация успешна
        """
        if personality.name in self._personalities:
            return False  # Личность с таким именем уже существует
        self._personalities[personality.name] = personality
        return True
    
    def get_personality_for_agent_md(self, agent_md_content: str) -> Optional[str]:
        """
        Извлекает личность из содержимого agents/*.md файла.
        
        Ищет секцию ## Personality в файле агента.
        
        Args:
            agent_md_content: Содержимое MD файла агента
        
        Returns:
            Имя личности или None, если секция не найдена
        """
        import re
        # Ищем секцию ## Personality
        pattern = r'##\s*Personality\s*\n(.*?)(?=\n##|\Z)'
        match = re.search(pattern, agent_md_content, re.IGNORECASE | re.DOTALL)
        
        if match:
            section_content = match.group(1).strip()
            # Ищем имя личности в содержимом секции
            for pname in self._personalities.keys():
                if pname.lower() in section_content.lower():
                    return pname
        return None


# Глобальный экземпляр менеджера
_default_manager: Optional[PersonalityManager] = None


def get_personality_manager() -> PersonalityManager:
    """
    Получает глобальный экземпляр менеджера личностей.
    
    Returns:
        Экземпляр PersonalityManager
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = PersonalityManager()
    return _default_manager


def get_personality_prompt(personality_name: str) -> str:
    """
    Удобная функция для получения модификатора личности.
    
    Args:
        personality_name: Имя личности
    
    Returns:
        Модификатор system prompt
    """
    manager = get_personality_manager()
    return manager.get_personality_prompt(personality_name)


def apply_personality_to_system_prompt(base_prompt: str, personality_name: str) -> str:
    """
    Применяет личность к system prompt.
    
    Args:
        base_prompt: Базовый system prompt
        personality_name: Имя личности
    
    Returns:
        Модифицированный system prompt
    """
    manager = get_personality_manager()
    personality = manager.get_personality(personality_name)
    
    if not personality:
        return base_prompt
    
    modifier = personality.system_prompt_modifier
    return f"{base_prompt}\n\n{modifier}"
