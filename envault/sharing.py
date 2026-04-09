"""Vault sharing: export an encrypted share bundle for another user."""

import json
import os
import base64
from pathlib import Path
from envault.crypto import CryptoManager


class SharingError(Exception):
    pass


class SharingManager:
    """Create and consume encrypted share bundles."""

    def __init__(self, vault):
        self._vault = vault

    def create_share(self, keys: list[str], share_password: str) -> dict:
        """Build an encrypted bundle containing the requested keys."""
        all_vars = self._vault.get_all()
        missing = [k for k in keys if k not in all_vars]
        if missing:
            raise SharingError(f"Keys not found in vault: {', '.join(missing)}")

        payload = {k: all_vars[k] for k in keys}
        crypto = CryptoManager(share_password)
        plaintext = json.dumps(payload).encode()
        ciphertext, salt = crypto.encrypt(plaintext)
        return {
            "version": 1,
            "salt": base64.b64encode(salt).decode(),
            "data": base64.b64encode(ciphertext).decode(),
        }

    def save_share(self, bundle: dict, path: str) -> None:
        """Persist a share bundle to a JSON file."""
        Path(path).write_text(json.dumps(bundle, indent=2))

    def load_share(self, path: str) -> dict:
        """Read a share bundle from a JSON file."""
        p = Path(path)
        if not p.exists():
            raise SharingError(f"Share file not found: {path}")
        return json.loads(p.read_text())

    def apply_share(self, bundle: dict, share_password: str, overwrite: bool = False) -> list[str]:
        """Decrypt a bundle and write its variables into the vault."""
        if bundle.get("version") != 1:
            raise SharingError("Unsupported share bundle version.")

        salt = base64.b64decode(bundle["salt"])
        ciphertext = base64.b64decode(bundle["data"])
        crypto = CryptoManager(share_password, salt=salt)
        try:
            plaintext = crypto.decrypt(ciphertext)
        except Exception as exc:
            raise SharingError("Decryption failed — wrong password?") from exc

        payload: dict = json.loads(plaintext.decode())
        imported = []
        for key, value in payload.items():
            existing = self._vault.get(key)
            if existing is not None and not overwrite:
                continue
            self._vault.set(key, value)
            imported.append(key)
        return imported
