"""Tests for APEX User Memory Vault."""

import pytest
from apex.core.database import db
from apex.core.memory import MemoryService


@pytest.fixture(autouse=True)
def clean_memories():
    """Ensure a clean memory database before and after each test."""
    db.clear_all_memories()
    MemoryService.set_paused(False)
    yield
    db.clear_all_memories()


def test_add_and_list_memories():
    """Verify adding memories and listing them."""
    m1 = MemoryService.add_memory("Prefers concise answers", category="preference")
    m2 = MemoryService.add_memory("Working on APEX project", category="project")

    memories = MemoryService.list_memories()
    assert len(memories) == 2
    ids = [m["id"] for m in memories]
    assert m1 in ids
    assert m2 in ids


def test_memory_category_and_search_filter():
    """Verify searching and filtering memories by category."""
    MemoryService.add_memory("Enjoys dark mode user interfaces", category="preference")
    MemoryService.add_memory("Target hardware is Intel Core i3", category="fact")
    MemoryService.add_memory("Project name is APEX", category="project")

    # Filter by category
    prefs = MemoryService.list_memories(category="preference")
    assert len(prefs) == 1
    assert "dark mode" in prefs[0]["content"]

    # Search keyword
    results = MemoryService.list_memories(search_query="Intel")
    assert len(results) == 1
    assert "i3" in results[0]["content"]

    # Search non-matching
    none_results = MemoryService.list_memories(search_query="QuantumComputer")
    assert len(none_results) == 0


def test_update_and_delete_memory():
    """Verify modifying and deleting individual memories."""
    m_id = MemoryService.add_memory("Initial fact", category="fact")

    # Update
    updated = MemoryService.update_memory(m_id, "Updated fact", new_category="profile")
    assert updated is True

    record = db.get_memory(m_id)
    assert record["content"] == "Updated fact"
    assert record["category"] == "profile"

    # Delete
    deleted = MemoryService.delete_memory(m_id)
    assert deleted is True
    assert db.get_memory(m_id) is None


def test_memory_pause_and_prompt_context():
    """Verify prompt context injection and respect for pause state."""
    assert MemoryService.get_context_for_prompt() is None

    MemoryService.add_memory("Prefers Python over JavaScript", category="preference")
    ctx = MemoryService.get_context_for_prompt()
    assert ctx is not None
    assert "Prefers Python over JavaScript" in ctx
    assert "Preference" in ctx

    # Pause memory
    MemoryService.set_paused(True)
    assert MemoryService.is_paused() is True
    assert MemoryService.get_context_for_prompt() is None

    # Resume memory
    MemoryService.set_paused(False)
    assert MemoryService.is_paused() is False
    assert MemoryService.get_context_for_prompt() is not None


def test_clear_all_memories():
    """Verify bulk purge of all user memories."""
    MemoryService.add_memory("Fact 1")
    MemoryService.add_memory("Fact 2")
    assert len(MemoryService.list_memories()) == 2

    cleared = MemoryService.clear_all()
    assert cleared == 2
    assert len(MemoryService.list_memories()) == 0
