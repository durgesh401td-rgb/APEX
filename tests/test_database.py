"""Tests for APEX core database persistence."""

import tempfile
from pathlib import Path
import pytest
from apex.core.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for test isolation."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_apex.db"
        yield Database(db_path=db_path)


def test_create_and_list_conversations(temp_db: Database):
    """Verify conversations can be created and listed."""
    c1 = temp_db.create_conversation("First Chat")
    c2 = temp_db.create_conversation("Second Chat")

    convs = temp_db.list_conversations()
    assert len(convs) == 2
    ids = [c["id"] for c in convs]
    assert c1 in ids
    assert c2 in ids


def test_messages_persistence(temp_db: Database):
    """Verify adding and retrieving messages in a conversation."""
    conv_id = temp_db.create_conversation("Test Chat")
    m1 = temp_db.add_message(conv_id, "user", "Hello Apex!")
    m2 = temp_db.add_message(conv_id, "assistant", "Hello! How can I assist you today?")

    messages = temp_db.get_messages(conv_id)
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello Apex!"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hello! How can I assist you today?"


def test_delete_conversation_cascades(temp_db: Database):
    """Verify deleting a conversation cascades to its messages."""
    conv_id = temp_db.create_conversation("To Delete")
    temp_db.add_message(conv_id, "user", "Ephemeral message")

    assert len(temp_db.get_messages(conv_id)) == 1
    temp_db.delete_conversation(conv_id)

    assert temp_db.get_conversation(conv_id) is None
    assert len(temp_db.get_messages(conv_id)) == 0


def test_settings_storage(temp_db: Database):
    """Verify key-value settings storage and upsert."""
    assert temp_db.get_setting("theme", default="dark") == "dark"
    temp_db.set_setting("theme", "midnight")
    assert temp_db.get_setting("theme") == "midnight"

    # Upsert test
    temp_db.set_setting("theme", "cyber_dark")
    assert temp_db.get_setting("theme") == "cyber_dark"
