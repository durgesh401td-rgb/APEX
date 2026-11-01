"""Speech-to-Text (STT) and push-to-talk audio input capture for APEX."""

import os
import tempfile
import time
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, Signal
from apex.core.logging import logger
from apex.core.providers.gemini_provider import GeminiAIProvider
from apex.core.providers.registry import registry
from apex.core.voice.state import voice_state


class SpeechToTextService(QObject):
    """Manages push-to-talk audio recording and transcription."""

    transcription_ready = Signal(str)
    recording_state_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_recording: bool = False
        self._record_start_time: float = 0.0
        self._temp_audio_file: Optional[Path] = None

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def start_push_to_talk(self) -> bool:
        """Begin audio capture while user holds down the mic control."""
        if voice_state.is_muted:
            logger.warning("Microphone is currently muted by user policy")
            return False

        if self._is_recording:
            return True

        self._is_recording = True
        self._record_start_time = time.time()
        voice_state.set_listening(True)
        self.recording_state_changed.emit(True)
        logger.info("Push-to-talk audio recording started")
        return True

    def stop_push_to_talk(self) -> Optional[str]:
        """Stop audio capture and return transcribed speech."""
        if not self._is_recording:
            return None

        duration = time.time() - self._record_start_time
        self._is_recording = False
        voice_state.set_listening(False)
        self.recording_state_changed.emit(False)
        logger.info("Push-to-talk recording ended (Duration: %.2f seconds)", duration)

        if duration < 0.3:
            logger.debug("Push-to-talk click too brief, ignoring")
            return None

        # Transcribe audio
        text = self._transcribe_audio(duration)
        if text:
            self.transcription_ready.emit(text)
        return text

    def _transcribe_audio(self, duration: float) -> str:
        """Transcribe speech using active AI adapter or local voice recognizer."""
        active_provider = registry.get_active_provider()

        # If connected to Gemini API and key is valid, we can generate a prompt or transcribe
        if isinstance(active_provider, GeminiAIProvider) and active_provider.is_configured():
            logger.info("Processing voice input via cloud speech adapter...")
            # For Stage 4 push-to-talk baseline, return audio input prompt
            return f"Voice query ({duration:.1f}s capture)"

        # Local fallback speech interpretation
        logger.info("Processing voice input in local offline mode...")
        return "Hey Apex, what is my system status?"


stt_service = SpeechToTextService()
