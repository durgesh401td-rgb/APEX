"""Text-to-Speech (TTS) engine for APEX using native Windows SAPI5."""

import queue
import threading
from typing import Optional
from apex.core.logging import logger
from apex.core.voice.state import voice_state


class TextToSpeechService:
    """Non-blocking speech synthesis service configured with deep, calm male voice."""

    def __init__(self):
        self._queue = queue.Queue()
        self._stop_requested = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None
        self._engine = None
        self._is_ready = False
        self._start_worker()

    def _start_worker(self) -> None:
        """Start the background speech synthesis thread."""
        self._worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self._worker_thread.start()

    def _init_engine(self) -> None:
        """Initialize pyttsx3 SAPI5 engine inside the worker thread."""
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            # Set rate: slightly relaxed (165 wpm) for a calm, professional delivery
            self._engine.setProperty("rate", 165)
            # Set volume
            self._engine.setProperty("volume", 0.9)

            # Select deep, calm male voice (Microsoft David Desktop) if available
            voices = self._engine.getProperty("voices")
            for v in voices:
                if "david" in v.name.lower() or "male" in v.name.lower():
                    self._engine.setProperty("voice", v.id)
                    logger.info("Configured TTS voice: %s", v.name)
                    break

            self._is_ready = True
        except Exception as e:
            logger.warning("TTS initialization failed: %s (Audio speech will be disabled)", e)
            self._is_ready = False

    def _run_loop(self) -> None:
        """Background queue processor for speaking sentences."""
        self._init_engine()
        while True:
            text = self._queue.get()
            if text is None:
                break

            if not self._is_ready or not self._engine:
                self._queue.task_done()
                continue

            if not voice_state.tts_enabled:
                self._queue.task_done()
                continue

            try:
                self._stop_requested.clear()
                voice_state.set_speaking(True)
                logger.info("Speaking TTS response: '%s...'", text[:35])

                # Clean markdown characters for cleaner audio output
                clean_text = self._clean_markdown(text)
                self._engine.say(clean_text)
                self._engine.runAndWait()
            except Exception as e:
                logger.error("Error during speech playback: %s", e)
            finally:
                voice_state.set_speaking(False)
                self._queue.task_done()

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Strip markdown symbols (asterisks, hashtags, backticks) for smooth speech."""
        for ch in ["*", "#", "`", "_", ">", "[", "]", "(", ")"]:
            text = text.replace(ch, "")
        return text.strip()

    def speak(self, text: str) -> None:
        """Queue text to be spoken aloud by APEX."""
        if not text or not voice_state.tts_enabled:
            return
        # Stop any currently speaking queue before starting new utterance
        self.stop()
        self._queue.put(text)

    def stop(self) -> None:
        """Immediately interrupt in-flight speech."""
        self._stop_requested.set()
        try:
            while not self._queue.empty():
                self._queue.get_nowait()
                self._queue.task_done()
        except Exception:
            pass

        if self._engine and self._is_ready:
            try:
                self._engine.stop()
            except Exception:
                pass
        voice_state.set_speaking(False)


# Global TTS instance
tts_service = TextToSpeechService()
