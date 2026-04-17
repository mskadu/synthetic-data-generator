# AGENTS.md

## Project Overview
- **Name**: synthetic-data-generator
- **Type**: Python package
- **Test Framework**: pytest

## Development Commands
Use **uv** for dependency management (not pip).

- Always initialize a git repo (`git init`) if one doesn't exist when starting work.

```bash
# Initialize git if needed
git init

```bash
# Install in editable mode
uv pip install -e ".[dev]"

# Run tests
pytest

# Lint and format
ruff check .
ruff format .

# Pre-commit hooks
uv run pre-commit install
```

## LSP
- Pyright—use for inline errors, completions, and hover info

## Structure
- Single package: place code in `src/` or root with `pyproject.toml`
- Tests in `tests/` directory

## README
- If one doesn't exist, create a README.md with the following sections:
  - Name and description
  - Usage with examples
  - CLI parameters list and description
  - Changelog (version-wise changes)
  - Known bugs (if any)
  - Known limitations
- If README exists, keep it up to date with new features
- Increment version in `pyproject.toml` after every commit:
  - Patch (x.y.Z) for bug fixes and small changes
  - Minor (x.Y.0) for new features
  - Major (X.0.0) for breaking changes
  - Ask user to confirm if unsure which to use

## Notes
- Update with actual commands once tooling is configured