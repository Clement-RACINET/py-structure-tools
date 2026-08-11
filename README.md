# py-structure-tools

Print and export repository structures with zero runtime dependencies.

`py-structure-tools` is a small CLI utility designed to inspect, print, and export
the structure of a repository. It is especially useful for onboarding,
architecture reviews, documentation snapshots, and sharing a clean overview of a
project layout.

The package intentionally has **no runtime dependency**: it only relies on the
Python standard library.

---

## Features

- Print a repository tree in the terminal.
- Export repository structure to multiple formats:
  - TXT
  - JSON
  - YAML
  - XML
  - HTML
- Respect `.gitignore` patterns using stdlib-only matching.
- Configure exclusions from CLI options.
- Configure default behavior from `pyproject.toml`.
- Limit output depth with `--max-depth`.
- Include or exclude hidden files and directories.
- Generate a standalone interactive HTML tree.
- No runtime dependency.

---

## Installation

### From a Git repository

```bash
pip install git+https://gitlab.com/dev-tools-cr/python/py-structure-tools.git
```

### With Pixi

In another project, add the package as a PyPI Git dependency:

```toml
[pypi-dependencies]
py-structure-tools = { git = "https://gitlab.com/dev-tools-cr/python/py-structure-tools.git" }
```

Then install or update the environment:

```bash
pixi update
```

### Local editable installation

From this repository:

```bash
pip install -e .
```

Or with Pixi:

```bash
pixi install
```

---

## Usage

### Print the current repository tree

```bash
pystructure tree
```

### Print a specific root directory

```bash
pystructure tree --root .
```

### Limit tree depth

```bash
pystructure tree --root . --max-depth 3
```

### Include hidden files and directories

```bash
pystructure tree --include-hidden
```

### Ignore `.gitignore` rules

```bash
pystructure tree --no-gitignore
```

### Exclude directories from the CLI

```bash
pystructure tree --exclude-dir sandbox --exclude-dir litterature
```

### Exclude files from the CLI

```bash
pystructure tree --exclude-file "*.log" --exclude-file "*.tmp"
```

---

## Export

### Export using configured default formats

```bash
pystructure export
```

### Export all supported formats

```bash
pystructure export --formats all
```

### Export selected formats

```bash
pystructure export --formats txt html
```

### Export to a specific output directory

```bash
pystructure export --formats txt html --output-dir .
```

### Customize output basename

```bash
pystructure export --formats all --basename structure_repo
```

This generates files such as:

```text
structure_repo.txt
structure_repo.json
structure_repo.yaml
structure_repo.xml
structure_repo.html
```

### Configure HTML open depth

```bash
pystructure export --formats html --open-depth 2
```

---

## Supported export formats

| Format | Extension | Description                                                    |
| ------ | --------- | -------------------------------------------------------------- |
| TXT    | `.txt`    | Plain Unicode tree representation.                             |
| JSON   | `.json`   | Structured machine-readable tree.                              |
| YAML   | `.yaml`   | Human-readable structured tree without PyYAML.                 |
| XML    | `.xml`    | XML tree representation.                                       |
| HTML   | `.html`   | Standalone interactive tree using `<details>` and `<summary>`. |

---

## Configuration

`py-structure-tools` can be configured from the target project's
`pyproject.toml` file.

```toml
[tool.py-structure-tools]
exclude_dirs = [
    "sandbox",
    "litterature",
    "docs",
    "site",
]

exclude_files = [
    "*.log",
    "*.tmp",
]

include_hidden = false
use_gitignore = true
max_depth = 5
default_formats = ["txt", "html"]
output_basename = "structure_repo"
```

### Configuration options

| Option            | Type           | Default            | Description                                                       |
| ----------------- | -------------- | ------------------ | ----------------------------------------------------------------- |
| `exclude_dirs`    | `list[str]`    | Built-in defaults  | Directory names to exclude.                                       |
| `exclude_files`   | `list[str]`    | Built-in defaults  | File glob patterns to exclude.                                    |
| `include_hidden`  | `bool`         | `false`            | Include paths starting with `.`.                                  |
| `use_gitignore`   | `bool`         | `true`             | Apply root `.gitignore` patterns.                                 |
| `max_depth`       | `int` or unset | unset              | Maximum depth to traverse.                                        |
| `default_formats` | `list[str]`    | `["txt"]`          | Formats used by `pystructure export` when `--formats` is omitted. |
| `output_basename` | `str`          | `"structure_repo"` | Basename used for generated export files.                         |

---

## Default exclusions

The tool excludes common development/cache directories by default, including:

```text
.git
.hg
.svn
.pixi
.venv
venv
__pycache__
.pytest_cache
.ruff_cache
.mypy_cache
.tox
node_modules
__pypackages__
```

Default excluded files include:

```text
*.pyc
*.pyo
*.pyd
.coverage
coverage.xml
```

Project-specific folders such as `docs`, `site`, `sandbox`, or `litterature`
should be configured in the target project's `pyproject.toml` rather than baked
into global defaults.

---

## CLI reference

```text
pystructure tree [OPTIONS]
pystructure export [OPTIONS]
```

### Common options

```text
--root PATH
--max-depth INT
--include-hidden
--no-gitignore
--exclude-dir NAME
--exclude-file PATTERN
```

### Export options

```text
--output-dir PATH
--basename NAME
--formats txt json yaml xml html all
--open-depth INT
```

---

## Development

This repository uses Pixi for development tasks.

### Install the environment

```bash
pixi install
```

### Run formatting

```bash
pixi run fmt
```

### Run linting

```bash
pixi run lint
```

### Run type checking

```bash
pixi run typecheck
```

### Run tests

```bash
pixi run tests
```

### Run the full check suite

```bash
pixi run check
```

---

## Design principles

- **Zero runtime dependency**: only the Python standard library is used.
- **Single traversal engine**: terminal output and exports use the same tree model.
- **Predictable exclusions**: defaults, config, and CLI options are combined clearly.
- **Portable output**: exported files can be committed, shared, or attached to reviews.
- **Strict development quality**: linting, typing, and tests are part of the workflow.

---

## License

Copyright (c) 2026 Clement RACINET

This project is distributed under the MIT License with an additional
no-endorsement clause.

See [`LICENSE`](LICENSE) for details.

````

---

## Dernière commande avant commit

Après remplacement du fichier :

```powershell
pixi run lint
pixi run tests
````

Puis :

```powershell
git add README.md
git commit -m "docs: expand README"
```

Si tu n’as pas encore fait le commit initial, garde tout dans le même commit :

```powershell
git add -A
git commit -m "feat: add repository structure printer and exporters"
```
