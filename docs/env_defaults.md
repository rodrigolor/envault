# Environment Variable Defaults

The **defaults** feature lets you register fallback values for environment
variables. When a key is absent from the vault, `apply` will write the
default value so that your application always has a sensible starting
configuration.

## CLI Usage

### Register a default

```bash
envault defaults set LOG_LEVEL INFO
envault defaults set PORT 8080
```

### List all defaults

```bash
envault defaults list
# LOG_LEVEL=INFO
# PORT=8080
```

### Apply defaults to the vault

Only keys that are **not already present** in the vault will be written.

```bash
envault defaults apply
# Applied: LOG_LEVEL=INFO
# Applied: PORT=8080
```

### Remove a default

```bash
envault defaults remove LOG_LEVEL
```

## Python API

```python
from envault.env_defaults import DefaultsManager

mgr = DefaultsManager("/path/to/vault-dir")

mgr.set_default("DB_HOST", "localhost")
mgr.set_default("DB_PORT", "5432")

# Apply to an open vault
applied = mgr.apply(vault)
print(applied)  # {"DB_HOST": "localhost", "DB_PORT": "5432"}

# Query a single default
print(mgr.get_default("DB_HOST"))  # localhost

# Remove a default
mgr.remove_default("DB_HOST")
```

## Storage

Defaults are persisted in `defaults.json` inside the vault directory.
The file is plain JSON and can be committed to version control alongside
other vault metadata.

## Notes

- Default values are always stored and returned as strings.
- `apply` is idempotent — running it multiple times will not overwrite
  values that were set after the first run.
