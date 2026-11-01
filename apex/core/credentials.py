"""Secure OS-backed credential storage using Windows Credential Manager."""

from typing import Optional
import keyring
from keyring.errors import KeyringError
from apex.core.logging import logger

SERVICE_NAME = "APEX_AI_ASSISTANT"


class CredentialManager:
    """Manages sensitive credentials via OS-backed secure storage."""

    @staticmethod
    def save_credential(key_name: str, secret_value: str) -> bool:
        """Store a secret securely in Windows Credential Manager."""
        if not key_name or not secret_value:
            return False
        try:
            keyring.set_password(SERVICE_NAME, key_name, secret_value)
            logger.info("Credential '%s' securely stored in OS vault", key_name)
            return True
        except KeyringError as e:
            logger.error("Failed to store credential '%s': %s", key_name, e)
            return False

    @staticmethod
    def get_credential(key_name: str) -> Optional[str]:
        """Retrieve a secret from Windows Credential Manager."""
        if not key_name:
            return None
        try:
            return keyring.get_password(SERVICE_NAME, key_name)
        except KeyringError as e:
            logger.error("Failed to retrieve credential '%s': %s", key_name, e)
            return None

    @staticmethod
    def delete_credential(key_name: str) -> bool:
        """Remove a credential from Windows Credential Manager."""
        if not key_name:
            return False
        try:
            keyring.delete_password(SERVICE_NAME, key_name)
            logger.info("Credential '%s' deleted from OS vault", key_name)
            return True
        except KeyringError as e:
            logger.warning("Could not delete credential '%s': %s", key_name, e)
            return False

    @staticmethod
    def has_credential(key_name: str) -> bool:
        """Check if a credential exists without logging its value."""
        val = CredentialManager.get_credential(key_name)
        return bool(val and len(val.strip()) > 0)


credentials = CredentialManager()
