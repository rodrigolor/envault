"""Key rotation support for envault vaults."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envault.crypto import CryptoManager
from envault.storage import LocalStorageBackend
from envault.audit import AuditLog


class RotationError(Exception):
    """Raised when key rotation fails."""


class KeyRotationManager:
    """Handles re-encryption of vault data with a new password."""

    def __init__(self, vault_path: Path, audit_log: Optional[AuditLog] = None):
        self.vault_path = Path(vault_path)
        self.audit = audit_log or AuditLog(self.vault_path / "audit.log")

    def rotate(self, old_password: str, new_password: str) -> int:
        """Re-encrypt all variables with a new password.

        Returns the number of variables rotated.
        Raises RotationError if decryption with old password fails.
        """
        storage = LocalStorageBackend(self.vault_path)

        if not storage.exists():
            raise RotationError("Vault does not exist at the given path.")

        raw = storage.load()
        old_crypto = CryptoManager(old_password)
        new_crypto = CryptoManager(new_password)

        try:
            plaintext = old_crypto.decrypt(raw)
        except Exception as exc:
            raise RotationError(f"Failed to decrypt vault with old password: {exc}") from exc

        data = json.loads(plaintext)
        rotated_count = len(data)

        new_ciphertext = new_crypto.encrypt(json.dumps(data))
        storage.save(new_ciphertext)

        self.audit.record("rotate", {"variables_rotated": rotated_count})
        return rotated_count

    def needs_rotation(self, password: str, max_age_days: int = 90) -> bool:
        """Check if the vault key is older than max_age_days based on audit log."""
        events = self.audit.read()
        rotation_events = [
            e for e in events if e.get("action") in ("rotate", "init")
        ]
        if not rotation_events:
            return True
        import datetime
        last = rotation_events[-1]
        ts = last.get("timestamp", "")
        if not ts:
            return True
        try:
            last_dt = datetime.datetime.fromisoformat(ts)
            age = (datetime.datetime.utcnow() - last_dt).days
            return age >= max_age_days
        except ValueError:
            return True
