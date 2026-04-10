"""Backup and restore vault data to/from archive files."""

import json
import zipfile
import io
from pathlib import Path
from datetime import datetime
from typing import Optional


class BackupError(Exception):
    pass


class BackupManager:
    MANIFEST_NAME = "manifest.json"
    DATA_NAME = "vault_data.json"

    def __init__(self, vault, backup_dir: Path):
        self.vault = vault
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create(self, label: Optional[str] = None) -> Path:
        """Create a backup archive of current vault data."""
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        name = f"backup_{label}_{timestamp}.zip" if label else f"backup_{timestamp}.zip"
        archive_path = self.backup_dir / name

        try:
            data = self.vault.get_all()
        except Exception as exc:
            raise BackupError(f"Failed to read vault data: {exc}") from exc

        manifest = {
            "created_at": timestamp,
            "label": label,
            "key_count": len(data),
        }

        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(self.MANIFEST_NAME, json.dumps(manifest, indent=2))
            zf.writestr(self.DATA_NAME, json.dumps(data, indent=2))

        return archive_path

    def restore(self, archive_path: Path, overwrite: bool = False) -> int:
        """Restore vault data from a backup archive. Returns number of keys restored."""
        archive_path = Path(archive_path)
        if not archive_path.exists():
            raise BackupError(f"Backup file not found: {archive_path}")

        try:
            with zipfile.ZipFile(archive_path, "r") as zf:
                names = zf.namelist()
                if self.DATA_NAME not in names:
                    raise BackupError("Archive is missing vault data file.")
                raw = zf.read(self.DATA_NAME)
                data = json.loads(raw)
        except (zipfile.BadZipFile, json.JSONDecodeError) as exc:
            raise BackupError(f"Failed to read backup archive: {exc}") from exc

        existing = self.vault.get_all()
        restored = 0
        for key, value in data.items():
            if key in existing and not overwrite:
                continue
            self.vault.set(key, value)
            restored += 1

        return restored

    def list_backups(self) -> list:
        """Return sorted list of backup archive paths (newest first)."""
        return sorted(
            self.backup_dir.glob("backup_*.zip"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
