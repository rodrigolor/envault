"""Vault manager for storing and retrieving environment variables."""

import json
from typing import Dict, Optional

from envault.crypto import CryptoManager
from envault.storage import StorageBackend, LocalFileStorage


class Vault:
    """Manages encrypted environment variable storage."""

    def __init__(self, password: str, storage: Optional[StorageBackend] = None):
        """Initialize vault with password and storage backend.
        
        Args:
            password: Master password for encryption/decryption
            storage: Storage backend (defaults to LocalFileStorage)
        """
        self.crypto = CryptoManager(password)
        self.storage = storage or LocalFileStorage()

    def set(self, key: str, value: str) -> None:
        """Set an environment variable in the vault.
        
        Args:
            key: Environment variable name
            value: Environment variable value
        """
        env_vars = self.get_all() or {}
        env_vars[key] = value
        self._save_all(env_vars)

    def get(self, key: str) -> Optional[str]:
        """Get an environment variable from the vault.
        
        Args:
            key: Environment variable name
            
        Returns:
            Variable value or None if not found
        """
        env_vars = self.get_all()
        if env_vars is None:
            return None
        return env_vars.get(key)

    def get_all(self) -> Optional[Dict[str, str]]:
        """Get all environment variables from the vault.
        
        Returns:
            Dictionary of all variables or None if vault is empty
        """
        encrypted_data = self.storage.load()
        if encrypted_data is None:
            return None
        
        decrypted_json = self.crypto.decrypt(encrypted_data)
        return json.loads(decrypted_json)

    def delete(self, key: str) -> bool:
        """Delete an environment variable from the vault.
        
        Args:
            key: Environment variable name
            
        Returns:
            True if variable was deleted, False if not found
        """
        env_vars = self.get_all()
        if env_vars is None or key not in env_vars:
            return False
        
        del env_vars[key]
        self._save_all(env_vars)
        return True

    def _save_all(self, env_vars: Dict[str, str]) -> None:
        """Save all environment variables to storage.
        
        Args:
            env_vars: Dictionary of environment variables
        """
        json_data = json.dumps(env_vars, indent=2)
        encrypted_data = self.crypto.encrypt(json_data)
        self.storage.save(encrypted_data)

    def clear(self) -> None:
        """Clear all data from the vault."""
        self.storage.delete()
