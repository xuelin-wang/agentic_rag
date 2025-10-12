# AGENTS.md

## Repository Conventions
- Python 3.12; package manager: `uv`.
- Lint & format with Ruff.
- Always run before committing:
  1. `uvx ruff check --fix .`
  2. `uvx ruff format .`

## Default Tasks
- **Style fix**: Run `make fix && make format` (Makefile targets exist).
- **Pre-commit**: If missing, install with `uvx pre-commit install`.

## Pull Request Policy
- CI requires `uvx ruff check .` and `uvx ruff format --check .` to pass.

