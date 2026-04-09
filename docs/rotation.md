# Key Rotation

Key rotation allows you to re-encrypt your vault with a new password without losing any stored variables. This is a security best practice and should be done periodically.

## Why Rotate?

- A team member who knew the old password has left
- You suspect the password may have been compromised
- Your security policy requires periodic credential rotation

## CLI Usage

### Rotate the vault key

```bash
envault rotate run --vault-path .envault
```

You will be prompted for the current password and the new password (with confirmation).

```
Current vault password: ****
New vault password: ****
Repeat for confirmation: ****
✓ Key rotation complete. 5 variable(s) re-encrypted.
```

### Check if rotation is recommended

```bash
envault rotate check --vault-path .envault --max-age 90
```

This checks the audit log to determine when the last rotation occurred. If it exceeds `--max-age` days (default: 90), a warning is shown.

```
⚠ Key rotation is recommended (threshold: 90 days).
```

or

```
✓ Key is within the acceptable age range.
```

## Programmatic Usage

```python
from pathlib import Path
from envault.rotation import KeyRotationManager, RotationError

mgr = KeyRotationManager(Path(".envault"))

try:
    count = mgr.rotate(old_password="old-secret", new_password="new-secret")
    print(f"Rotated {count} variables.")
except RotationError as e:
    print(f"Rotation failed: {e}")
```

## Audit Trail

Every rotation is recorded in the audit log with a timestamp and the number of variables re-encrypted. Use `envault audit` commands to inspect the history.

## Notes

- Rotation is atomic at the storage level: the vault file is only overwritten after successful re-encryption.
- Always back up your vault before rotating if you are unsure of the old password.
