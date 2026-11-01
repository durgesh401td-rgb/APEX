"""Structured logging system for APEX with security/privacy guardrails."""

import logging
import re
import sys
from typing import Optional
from apex.core.config import config

# Secret redaction patterns: (regex, replacement)
SECRET_REPLACEMENTS = [
    (re.compile(r"((?:api[_-]?key|token|secret|password|bearer\s+)['\":=\s]+)[a-zA-Z0-9_\-\.]{8,}", re.IGNORECASE), r"\1[REDACTED]"),
    (re.compile(r"AIzaSy[a-zA-Z0-9_\-]{33}"), "[REDACTED]"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "[REDACTED]"),
]


class SensitiveDataFilter(logging.Filter):
    """Filter to ensure no passwords, API keys, or personal tokens leak into logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.sanitize(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.sanitize(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self.sanitize(str(arg)) for arg in record.args)
        return True

    @staticmethod
    def sanitize(text: str) -> str:
        for pattern, replacement in SECRET_REPLACEMENTS:
            text = pattern.sub(replacement, text)
        return text


_logger_initialized = False


def setup_logging(log_level: int = logging.INFO) -> logging.Logger:
    """Initialize and configure structured logging for APEX."""
    global _logger_initialized
    root_logger = logging.getLogger("apex")

    if _logger_initialized:
        return root_logger

    root_logger.setLevel(log_level)
    root_logger.propagate = False

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s:%(funcName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    sensitive_filter = SensitiveDataFilter()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(sensitive_filter)
    root_logger.addHandler(console_handler)

    # File Handler
    try:
        config.log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(config.log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(sensitive_filter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        console_handler.handle(
            root_logger.makeRecord(
                "apex", logging.WARNING, __file__, 0,
                f"Failed to initialize file logger: {e}", (), None
            )
        )

    _logger_initialized = True
    root_logger.info("Logging initialized for APEX v%s", config.version)
    return root_logger


logger = setup_logging()
