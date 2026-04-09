# Vault Diff

The `diff` feature lets you compare your current vault state against a saved
JSON snapshot, or compare two snapshot files with each other.

## Commands

### `envault diff snapshot <file>`

Compare the live vault against a JSON snapshot file.

```bash
# Text output (default)
envault diff snapshot ./backup.json --password mysecret

# JSON output
envault diff snapshot ./backup.json --password mysecret --format json
```

**Output legend**

| Prefix | Meaning |
|--------|---------|
| `+`    | Key exists in vault but **not** in snapshot (added) |
| `-`    | Key exists in snapshot but **not** in vault (removed) |
| `~`    | Key exists in both but values differ (modified) |

### `envault diff files <file_a> <file_b>`

Compare two JSON snapshot files without touching the live vault.

```bash
envault diff files ./snap_2024-01.json ./snap_2024-02.json
```

## Snapshot format

Snapshots are plain JSON objects mapping variable names to their values:

```json
{
  "DATABASE_URL": "postgres://localhost/mydb",
  "SECRET_KEY": "s3cr3t"
}
```

You can generate a snapshot with `envault export dump --format json`.

## Programmatic usage

```python
from envault.diff import DiffManager

manager = DiffManager(vault)
result = manager.compare({"DATABASE_URL": "old_value"})

if result.has_changes:
    print(result.summary())
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | Command ran successfully (changes may or may not exist) |
| 1    | An error occurred (bad file, vault unavailable, etc.) |
