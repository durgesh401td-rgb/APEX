"""Centralized voice and microphone state management for APEX."""

from typing import Callable, List
from apex.core.database import db
from apex.core.logging import logger

SETTING_VOICE_MUTED = "voice_muted"
SETTING_TTS_ENABLED = "tts_enabled"


class VoiceState:
    """Tracks microphone and audio playback state with observer notification."""

    def __init__(self):
        self._is_listening: bool = False
        self._is_speaking: bool = False
        self._listeners: List[Callable[[str, bool], None]] = []

    @property
    def is_listening(self) -> bool:
        return self._is_listening

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    @property
    def is_muted(self) -> bool:
        """Physical/software mute state."""
        val = db.get_setting(SETTING_VOICE_MUTED, default="false")
        return val.lower() in ("true", "1", "yes")

    @property
    def tts_enabled(self) -> bool:
        """Whether APEX should read out AI responses aloud."""
        val = db.get_setting(SETTING_TTS_ENABLED, default="true")
        return val.lower() in ("true", "1", "yes")

    def set_muted(self, muted: bool) -> None:
        """Set software mute state."""
        db.set_setting(SETTING_VOICE_MUTED, "true" if muted else "false")
        logger.info("Microphone mute set to %s", muted)
        self._notify("muted", muted)

    def set_tts_enabled(self, enabled: bool) -> None:
        """Enable or disable text-to-speech audio output."""
        db.set_setting(SETTING_TTS_ENABLED, "true" if enabled else "false")
        logger.info("TTS voice playback enabled=%s", enabled)
        self._notify("tts_enabled", enabled)

    def set_listening(self, listening: bool) -> None:
        """Update active microphone recording state."""
        if self._is_listening != listening:
            self._is_listening = listening
            logger.debug("Voice listening state: %s", listening)
            self._notify("listening", listening)

    def set_speaking(self, speaking: bool) -> None:
        """Update active text-to-speech playback state."""
        if self._is_speaking != speaking:
            self._is_speaking = speaking
            logger.debug("Voice speaking state: %s", speaking)
            self._notify("speaking", speaking)

    def add_listener(self, callback: Callable[[str, bool], None]) -> None:
        """Register a callback for state changes (event_name, new_value)."""
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[str, bool], None]) -> None:
        """Unregister a state listener callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self, event: str, value: bool) -> None:
        dead_listeners = []
        for cb in self._listeners:
            try:
                cb(event, value)
            except RuntimeError:
                # Underlying Qt C++ object was destroyed
                dead_listeners.append(cb)
            except Exception as e:
                logger.error("Error invoking voice state listener: %s", e)

        for dead in dead_listeners:
            if dead in self._listeners:
                self._listeners.remove(dead)


voice_state = VoiceState()
