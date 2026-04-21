# Compliance Policies

The `compliance` module allows you to define and enforce policies on your environment variables, ensuring they meet organizational or security standards before deployment.

## Supported Rules

| Rule | Type | Description |
|------|------|-------------|
| `no_plaintext_secret` | bool | Flags keys containing secret-like names (e.g. `PASSWORD`, `TOKEN`) with short values |
| `key_uppercase` | bool | Requires all variable keys to be uppercase |
| `no_empty_value` | bool | Disallows empty string values |
| `max_length` | int | Enforces a maximum character length on values |

## CLI Usage

### Set a Policy

```bash
envault compliance set key_uppercase true
envault compliance set max_length 256
envault compliance set no_empty_value true
envault compliance set no_plaintext_secret true
```

### Remove a Policy

```bash
envault compliance remove key_uppercase
```

### List Active Policies

```bash
envault compliance list
```

Example output:
```
  key_uppercase: True
  max_length: 256
```

### Run Compliance Check

```bash
envault compliance check
```

This checks all variables in the current vault against active policies.

Example output (passing):
```
All checks passed. No violations found.
```

Example output (failing):
```
3 violation(s) found.
  - [key_uppercase] db_host: Key must be uppercase
  - [no_empty_value] API_URL: Value must not be empty
  - [no_plaintext_secret] DB_PASSWORD: Possible plaintext secret detected
```

The command exits with code `1` when violations are found, making it suitable for use in CI/CD pipelines.

## Python API

```python
from envault.env_compliance import ComplianceManager

mgr = ComplianceManager(".envault")
mgr.set_policy("key_uppercase", True)
mgr.set_policy("no_empty_value", True)

variables = {"MY_KEY": "value", "bad_key": ""}
result = mgr.check(variables)

if not result.is_compliant:
    for violation in result.violations:
        print(violation)
```

## Integration with CI/CD

Add a compliance check step to your pipeline:

```yaml
- name: Compliance Check
  run: envault compliance check
```

The non-zero exit code on failure will automatically fail the pipeline step.
