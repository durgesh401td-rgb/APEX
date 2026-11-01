"""User-controlled long-term memory management for APEX."""

from typing import Any, Dict, List, Optional
from apex.core.database import db
from apex.core.logging import logger

SETTING_MEMORY_PAUSED = "memory_paused"


class MemoryService:
    """Manages user-approved facts, preferences, and prompt context injection."""

    @staticmethod
    def is_paused() -> bool:
        """Check if memory retrieval and storage are currently paused by the user."""
        val = db.get_setting(SETTING_MEMORY_PAUSED, default="false")
        return val.lower() in ("true", "1", "yes")

    @staticmethod
    def set_paused(paused: bool) -> None:
        """Pause or resume memory operations."""
        db.set_setting(SETTING_MEMORY_PAUSED, "true" if paused else "false")
        logger.info("Memory service state set to paused=%s", paused)

    @staticmethod
    def add_memory(content: str, category: str = "general", source: str = "user_explicit") -> str:
        """Add a verified memory fact."""
        return db.add_memory(content=content, category=category, source=source)

    @staticmethod
    def list_memories(search_query: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List stored memories with optional filtering."""
        return db.list_memories(search_query=search_query, category=category)

    @staticmethod
    def update_memory(memory_id: str, new_content: str, new_category: Optional[str] = None) -> bool:
        """Update an existing memory entry."""
        return db.update_memory(memory_id=memory_id, new_content=new_content, new_category=new_category)

    @staticmethod
    def delete_memory(memory_id: str) -> bool:
        """Delete an individual memory record."""
        return db.delete_memory(memory_id=memory_id)

    @staticmethod
    def clear_all() -> int:
        """Wipe all user memories."""
        return db.clear_all_memories()

    @staticmethod
    def get_context_for_prompt(max_items: int = 10) -> Optional[str]:
        """Format user-approved memories into prompt context for AI providers."""
        if MemoryService.is_paused():
            return None

        memories = db.list_memories()
        if not memories:
            return None

        # Take up to max_items most recently updated memories
        subset = memories[:max_items]
        lines = ["User-approved profile and preferences (Long-Term Memory):"]
        for m in subset:
            cat = m["category"].capitalize()
            lines.append(f"- [{cat}] {m['content']}")

        return "\n".join(lines)


memory_service = MemoryService()
