# envault

> A CLI tool to securely store and sync environment variables across machines using encrypted backends.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

**Push your local environment variables to the vault:**

```bash
envault push --env .env --project myapp
```

**Pull variables on another machine:**

```bash
envault pull --project myapp --output .env
```

**List stored projects:**

```bash
envault list
```

**Rotate encryption keys:**

```bash
envault rotate --project myapp
```

Variables are encrypted locally before being sent to the backend. Supported backends include the local filesystem, AWS S3, and HashiCorp Vault.

---

## Configuration

On first run, initialize envault with:

```bash
envault init
```

This creates a `~/.envault/config.toml` file where you can configure your preferred backend and encryption settings.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*Contributions welcome. Open an issue or submit a pull request.*