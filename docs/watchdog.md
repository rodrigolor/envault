# Vault Watchdog

The **watchdog** module lets you monitor specific vault keys for changes and
trigger callbacks automatically — useful for reloading configuration in
long-running processes or sending alerts when sensitive values are rotated.

## Quick Start

```python
from envault.vault import Vault
from envault.watchdog import VaultWatchdog

vault = Vault(vault_dir=".envault", password="s3cr3t")
wd = VaultWatchdog(vault, interval=10.0)  # poll every 10 seconds

def on_change(key, old_value, new_value):
    if new_value is None:
        print(f"{key} was deleted (was: {old_value})")
    else:
        print(f"{key} changed: {old_value!r} → {new_value!r}")

wd.watch("DATABASE_URL", on_change)
wd.watch("API_KEY", on_change)

wd.start()  # starts background thread

# ... your application runs ...

wd.stop()   # clean shutdown
```

## API Reference

### `VaultWatchdog(vault, interval=5.0)`

| Parameter  | Type    | Description                              |
|------------|---------|------------------------------------------|
| `vault`    | `Vault` | Any vault-like object with `get_all()`   |
| `interval` | `float` | Seconds between polls (default `5.0`)    |

### Methods

| Method                        | Description                                          |
|-------------------------------|------------------------------------------------------|
| `watch(key, callback)`        | Register a callback for changes to `key`             |
| `unwatch(key)`                | Remove all callbacks registered for `key`            |
| `start()`                     | Start the background polling thread                  |
| `stop()`                      | Stop the polling thread (blocks until joined)        |
| `is_running` *(property)*     | `True` while the polling thread is active            |

### Callback Signature

```python
def callback(key: str, old_value: str | None, new_value: str | None) -> None:
    ...
```

- `old_value` is `None` when the key did not exist before.
- `new_value` is `None` when the key has been deleted.

## Notes

- The watchdog only monitors keys that have been explicitly registered with
  `watch()`. Changes to other keys are silently ignored.
- Multiple callbacks can be registered for the same key; all are invoked in
  registration order.
- The polling thread is a **daemon thread** and will not prevent your process
  from exiting. Call `stop()` explicitly for a clean shutdown.
- `WatchdogError` is raised if `start()` is called while already running, or
  if the vault raises an exception during a poll cycle.
