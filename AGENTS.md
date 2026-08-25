# Repository Guidelines

## Project Structure & Module Organization

This repository is currently specification-first: `silver_price_bale_bot_prd.md` is the source of truth for behavior and architecture. Implement application code under `src/silver_bot/`, keeping orchestration in `service.py`, configuration in `config.py`, persistence in `database.py`, and each external provider in `src/silver_bot/sources/`. Place tests under `tests/`; store representative API payloads in `tests/fixtures/`. Keep deployment files (`Dockerfile`, `compose.yaml`, and `.env.example`) at the repository root.

## Build, Test, and Development Commands

The implementation and packaging files have not been added yet. Once present, use the PRD-defined entry points:

- `python -m silver_bot run` — start continuous polling.
- `python -m silver_bot once --dry-run` — fetch and aggregate without publishing to Bale.
- `python -m silver_bot doctor` — check configuration, SQLite, sources, and Bale credentials.
- `python -m pytest` — run the full test suite.
- `docker compose up --build -d` — build and start the production service.
- `docker compose logs` — inspect production logs from stdout/stderr.

Run Python commands with `src` installed as a package, or set `PYTHONPATH=src` during early development.

## Coding Style & Naming Conventions

Target Python 3.12 with four-space indentation and type hints on public functions. Use `snake_case` for modules, functions, and variables; `PascalCase` for classes; and uppercase names for environment variables. Represent every monetary value with `Decimal`, never `float`. Keep source-specific parsing inside its adapter; runtime code currently uses the Python standard library only.

## Testing Guidelines

Use `pytest` and `pytest-cov`. Name files `test_<module>.py` and tests `test_<behavior>`. Mock all HTTP calls; tests must not depend on live APIs or Bale. Cover adapter parsing and normalization, weighted aggregation and outliers, database writes, and Bale failures. Preserve a regression test proving all four source scales normalize to the same general price range.

## Commit & Pull Request Guidelines

History currently contains one short, imperative commit (`initialize the project`). Continue with focused imperative subjects such as `add Tokeniko adapter`. Pull requests should summarize behavior, reference the relevant PRD section or issue, list verification commands, and call out configuration or schema changes. Include screenshots only for user-visible output changes.

## Security & Configuration

Never commit `.env`, Bale tokens, database files, or raw responses containing secrets. Keep safe placeholders in `.env.example`, redact secrets from logs and exceptions, verify TLS, and expose no container ports.
