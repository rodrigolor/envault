"""Environment variable injection — load vault secrets into the current process environment."""

from __future__ import annotations

import os
from typing import Optional

from envault.vault import Vault


class InjectionError(Exception):
    """Raised when environment injection fails."""


class EnvInjector:
    """Injects vault secrets into os.environ (or a target dict)."""

    def __init__(self, vault: Vault) -> None:
        self._vault = vault

    def inject(
        self,
        *,
        prefix: str = "",
        overwrite: bool = False,
        target: Optional[dict] = None,
        keys: Optional[list[str]] = None,
    ) -> dict[str, str]:
        """Inject secrets into *target* (defaults to ``os.environ``).

        Args:
            prefix:    Optional prefix to prepend to every key name.
            overwrite: If False (default), existing env vars are preserved.
            target:    Mapping to inject into. Defaults to ``os.environ``.
            keys:      Explicit list of vault keys to inject; None means all.

        Returns:
            A dict of the key/value pairs that were actually injected.
        """
        if target is None:
            target = os.environ  # type: ignore[assignment]

        all_vars: dict[str, str] = self._vault.get_all()

        if keys is not None:
            missing = [k for k in keys if k not in all_vars]
            if missing:
                raise InjectionError(
                    f"Keys not found in vault: {', '.join(missing)}"
                )
            all_vars = {k: all_vars[k] for k in keys}

        injected: dict[str, str] = {}
        for key, value in all_vars.items():
            env_key = f"{prefix}{key}" if prefix else key
            if not overwrite and env_key in target:
                continue
            target[env_key] = value
            injected[env_key] = value

        return injected

    def eject(
        self,
        *,
        prefix: str = "",
        target: Optional[dict] = None,
    ) -> list[str]:
        """Remove previously injected secrets from *target*.

        Returns:
            List of env var names that were removed.
        """
        if target is None:
            target = os.environ  # type: ignore[assignment]

        all_keys = list(self._vault.get_all().keys())
        removed: list[str] = []
        for key in all_keys:
            env_key = f"{prefix}{key}" if prefix else key
            if env_key in target:
                del target[env_key]
                removed.append(env_key)
        return removed
