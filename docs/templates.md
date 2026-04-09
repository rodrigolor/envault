# Templates

Templates let you snapshot a set of environment variables and re-apply them
later — useful for bootstrapping new machines or switching between project
configurations quickly.

## Concepts

| Term | Description |
|------|-------------|
| Template | A named snapshot of key/value pairs |
| Save | Capture the current vault contents into a template |
| Apply | Write a template's variables back into the vault |

## CLI Usage

### Save the current vault as a template

```bash
envault template save <name> [--dir .envault] [--vault-dir .envault]
```

You will be prompted for the vault password. All variables currently in the
vault are stored under `<name>`.

### Apply a template to the vault

```bash
envault template apply <name> [--dir .envault] [--vault-dir .envault]
```

Variables defined in the template are written into the active vault,
overwriting any existing values for matching keys.

### List templates

```bash
envault template list [--dir .envault]
```

### Delete a template

```bash
envault template delete <name> [--dir .envault]
```

## Python API

```python
from envault.templates import TemplateManager

mgr = TemplateManager(".envault")

# Save
mgr.save_template("staging", {"DB_HOST": "db.staging.example.com"})

# Load
vars = mgr.load_template("staging")

# Apply to a vault instance
mgr.apply_template("staging", vault)

# List
print(mgr.list_templates())  # ['staging']

# Delete
mgr.delete_template("staging")
```

## Storage

Templates are persisted in `<base_dir>/templates.json` as plain JSON.
They are **not encrypted** — avoid storing sensitive default values directly
in templates; use placeholder strings instead.
