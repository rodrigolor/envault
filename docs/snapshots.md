# Vault Snapshots

Snapshots let you capture the entire state of a vault profile at a point in time and restore it later. This is useful before bulk changes, key rotations, or environment migrations.

## Concepts

- A **snapshot** is a named, timestamped copy of all key-value pairs currently stored in the vault.
- Snapshots are stored in `~/.envault/snapshots.json` (or the configured vault directory).
- Restoring a snapshot **overwrites** the current values for matching keys but does not delete keys that were added after the snapshot was taken.

## CLI Usage

### Create a snapshot

```bash
envault snapshot create <name>
```

Example:

```bash
envault snapshot create before-rotation
# Snapshot 'before-rotation' created.
```

### List snapshots

```bash
envault snapshot list
```

Output:

```
  before-rotation       2024-06-01T12:00:00+00:00  (5 keys)
  post-deploy           2024-06-02T08:30:00+00:00  (7 keys)
```

### Restore a snapshot

```bash
envault snapshot restore <name>
```

Example:

```bash
envault snapshot restore before-rotation
# Restored 5 variable(s) from snapshot 'before-rotation'.
```

### Delete a snapshot

```bash
envault snapshot delete <name>
```

## Python API

```python
from pathlib import Path
from envault.snapshots import SnapshotManager

mgr = SnapshotManager(vault, base_dir=Path("~/.envault").expanduser())

mgr.create("my-snapshot")
print(mgr.list_snapshots())
mgr.restore("my-snapshot")
mgr.delete("my-snapshot")
```

## Error Handling

`SnapshotError` is raised when:

- Creating a snapshot with a name that already exists.
- Restoring or deleting a snapshot that does not exist.

## Storage Format

Snapshots are stored as plain JSON:

```json
{
  "before-rotation": {
    "created_at": "2024-06-01T12:00:00+00:00",
    "variables": {
      "DATABASE_URL": "postgres://localhost/mydb",
      "API_KEY": "secret"
    }
  }
}
```
