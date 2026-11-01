"""Tests for APEX Voice Layer, Push-to-Talk, and TTS."""

import pytest
from apex.core.voice.state import VoiceState
from apex.core.voice.stt import SpeechToTextService
from apex.core.voice.tts import TextToSpeechService
from apex.ui.widgets.visualizer import ApexVisualizer


def test_voice_state_properties():
    """Verify voice state properties and observer notifications."""
    state = VoiceState()
    events_received = []

    def observer(event, val):
        events_received.append((event, val))

    state.add_listener(observer)

    # Test mute
    state.set_muted(True)
    assert state.is_muted is True
    assert ("muted", True) in events_received

    state.set_muted(False)
    assert state.is_muted is False

    # Test listening
    state.set_listening(True)
    assert state.is_listening is True
    assert ("listening", True) in events_received

    state.set_listening(False)
    assert state.is_listening is False

    # Test speaking
    state.set_speaking(True)
    assert state.is_speaking is True
    assert ("speaking", True) in events_received

    state.set_speaking(False)
    assert state.is_speaking is False


def test_tts_clean_markdown():
    """Verify markdown symbols are cleaned before speech synthesis."""
    raw = "**Hello** *world*! Here is `code` and [link](url)."
    cleaned = TextToSpeechService._clean_markdown(raw)
    assert "*" not in cleaned
    assert "`" not in cleaned
    assert "[" not in cleaned
    assert "Hello world!" in cleaned


def test_stt_push_to_talk_workflow():
    """Verify push-to-talk state transitions and mute gate."""
    stt = SpeechToTextService()
    state = VoiceState()

    # When muted, recording should be rejected
    state.set_muted(True)
    assert stt.start_push_to_talk() is False
    assert stt.is_recording is False

    # When unmuted, recording succeeds
    state.set_muted(False)
    assert stt.start_push_to_talk() is True
    assert stt.is_recording is True

    # Stopping returns transcription
    text = stt.stop_push_to_talk()
    assert stt.is_recording is False


def test_visualizer_states(qapp):
    """Verify visualizer handles all voice state transitions."""
    vis = ApexVisualizer()
    for s in ["idle", "listening", "thinking", "speaking", "muted"]:
        vis.set_state(s)
        assert vis._state == s
