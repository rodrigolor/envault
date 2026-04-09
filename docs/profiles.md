# Profiles

envault supports **named profiles** so you can maintain separate sets of
environment variables for different contexts (e.g. `default`, `dev`, `prod`,
`ci`).

## Concepts

| Term | Description |
|------|-------------|
| Profile | A named collection of encrypted env vars, stored in its own vault file |
| Default profile | The profile named `default`, always present, cannot be deleted |
| Vault file | `<base-dir>/<profile>.vault` — encrypted storage for one profile |
| Index file | `<base-dir>/.envault_profiles.json` — plain JSON listing known profiles |

## CLI Usage

```bash
# List all profiles
envault profile list

# Create a new profile
envault profile create prod

# Delete a profile (removes it from the index; vault file is kept)
envault profile delete staging
```

## Selecting a Profile

Pass `--profile <name>` to any `envault` command to target a specific profile:

```bash
envault --profile prod set DATABASE_URL postgres://...
envault --profile prod get DATABASE_URL
```

If `--profile` is omitted, the `default` profile is used.

## File Layout

```
~/.envault/
  .envault_profiles.json   # profile index
  default.vault            # default profile vault
  prod.vault               # prod profile vault
  dev.vault                # dev profile vault
```

## Notes

- Each profile is encrypted independently with its own salt.
- Deleting a profile from the index does **not** remove its `.vault` file on
  disk; you must remove it manually if desired.
- Profile names must be unique and are case-sensitive.
