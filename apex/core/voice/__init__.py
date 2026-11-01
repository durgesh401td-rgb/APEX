"""Voice and audio subsystem for APEX."""

from apex.core.voice.state import voice_state
from apex.core.voice.tts import tts_service

__all__ = ["voice_state", "tts_service"]
