# AGENTS.md

## Project Overview

This repository is a local-first NYC taxi MLOps lab.

Current focus:
- ingest raw NYC taxi parquet files into a local bronze layer
- transform data with `dbt` + `DuckDB`
- evolve toward a medallion architecture for ML training and evaluation

Primary prediction target:
- `trip_duration_minutes`

Key technologies currently present:
- Python `3.12+`
- `uv` for environment and dependency management
- `dbt-duckdb`
- DuckDB
- Jupyter notebooks for exploration
- Parquet files as local data artifacts

## Repository Layout

```text
nyc-taxi-mlops/
├── AGENTS.md
├── README.md
├── full-spec.md
├── phase-1-outcomes.md
├── pyproject.toml
├── uv.lock
├── data/
│   └── bronze/
├── dbt_taxi/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── bronze/
│   │   ├── silver/
│   │   └── gold/
│   ├── seeds/
│   ├── macros/
│   ├── tests/
│   └── snapshots/
├── notebooks/
│   └── 01_data_exploration.ipynb
└── src/
    └── ingest/
        └── fetch_taxi_data.py
```

## Architecture and Ownership Boundaries

Follow these boundaries when adding code:

- `src/` owns reusable Python application logic.
- `dbt_taxi/` owns SQL transformations, data tests, and dbt metadata.
- `notebooks/` is exploratory only. Do not treat notebook code as production code.
- Future orchestration code should call reusable code in `src/` or `dbt`, not embed business logic.

Do not put:
- ML training logic in `dbt`
- transformation logic in notebooks
- large transformation or feature logic directly in orchestrators

## Setup Commands

### Create or sync the environment

- Install dependencies: `uv sync`
- Add a package: `uv add <package>`
- Run a Python file: `uv run python <path/to/file.py>`

### Activate the local virtual environment if needed

- `source .venv/bin/activate`

## Data Ingestion Commands

Current ingestion entrypoint:
- `src/ingest/fetch_taxi_data.py`

Run example:

- `uv run python src/ingest/fetch_taxi_data.py --taxi-type yellow --year 2026 --month 1`
- overwrite existing local file: `uv run python src/ingest/fetch_taxi_data.py --taxi-type yellow --year 2026 --month 1 --overwrite`

Current local raw data output path:
- `data/bronze/`

Note:
- local parquet data under `data/` is ignored by Git and should not be committed

## dbt Workflow

All dbt commands should be run from `dbt_taxi/` unless explicitly using `--project-dir`.

### Common commands

- Parse project: `dbt parse`
- Run models: `dbt run`
- Run tests: `dbt test`
- Build everything: `dbt build`
- Seed CSV data: `dbt seed`
- Clean generated artifacts: `dbt clean`

### Example

- `cd dbt_taxi && dbt build`

### Current dbt conventions

- `bronze` models are materialized as `view`
- `silver` models are materialized as `view`
- `gold` models are materialized as `table`

These defaults are configured in `dbt_taxi/dbt_project.yml`.

## Testing Instructions

This repo is still early-stage. There is not yet a broad automated Python test suite.

Current validation methods:
- run dbt tests with `cd dbt_taxi && dbt test`
- run dbt builds with `cd dbt_taxi && dbt build`
- run targeted Python scripts directly with `uv run python ...`
- verify notebook-derived assumptions against `phase-1-outcomes.md`

If you change:
- ingestion logic: run the relevant ingestion command
- dbt SQL/models: run `dbt build` or at minimum `dbt run` and `dbt test`
- seeds: run `dbt seed` and then `dbt test`

When adding new logic, add tests where practical rather than relying only on notebooks.

## Code Style Guidelines

### Python

- Prefer small, reusable functions.
- Keep filesystem and URL handling explicit.
- Use `pathlib.Path` for local paths.
- Avoid unused imports and dead code.
- Avoid hardcoded relative data paths inside business logic when a shared config abstraction is available.
- Use clear CLI options for scripts.

### SQL / dbt

- Keep raw file access centralized through dbt sources when possible.
- Avoid hardcoded `read_parquet('../data/...')` patterns in models long term.
- Use `bronze` for raw staging, `silver` for cleaned data, `gold` for curated analytics or ML-ready outputs.
- Prefer readable CTE-based SQL.

### Notebooks

- Keep notebooks exploratory.
- If logic becomes repeatable or production-relevant, move it into `src/` or `dbt_taxi/`.

## Data and Modeling Rules

Current project rules derived from `phase-1-outcomes.md`:

### Target definition
- target is `trip_duration_minutes`
- derive from `tpep_dropoff_datetime - tpep_pickup_datetime`

### First-pass cleaning expectations
- require non-null pickup and dropoff timestamps
- require positive trip duration
- require positive trip distance
- remove negative fare and total amount values
- cap initial duration at 180 minutes
- cap initial distance at 50 miles

### Leakage rules
Do not use as features for pickup-time prediction:
- `tpep_dropoff_datetime`
- `trip_duration_minutes`
- other post-trip outcome fields

### Split strategy
- use chronological train/validation/test splits
- do not use random splits for the initial ML workflow

## Build and Generated Artifacts

Do not commit generated local artifacts.

Ignored at the repository level:
- `.venv/`
- `__pycache__/`
- `data/`
- `logs/`
- `.ipynb_checkpoints/`

Ignored in `dbt_taxi/`:
- `target/`
- `dbt_packages/`
- `logs/`
- `*.duckdb`
- `*.duckdb.wal`
- `*.duckdb.tmp/`
- `partial_parse.msgpack`

Before committing, check that generated files are not staged.

## Pull Request and Commit Guidance

This repo is currently on `main` and appears to be in an early bootstrap phase.

Before committing changes:
- keep commits focused by concern
- separate docs/config changes from logic changes when practical
- do not commit local data files, local DuckDB databases, logs, or cache files
- run the relevant validation commands for the files you touched

Suggested commit style:
- `docs: add project planning notes`
- `feat: add taxi ingestion CLI`
- `feat: add bronze dbt model`
- `chore: update gitignore`

## Troubleshooting Notes

### dbt path issues
- Run dbt from `dbt_taxi/`.
- If file path resolution breaks, check the current working directory first.

### Local data issues
- If an ingestion run appears to succeed but dbt cannot find files, verify the parquet files exist under `data/bronze/`.
- Be careful with relative paths between the repo root and `dbt_taxi/`.

### Early codebase caveat
Current `src/ingest/fetch_taxi_data.py` should be reviewed carefully before extending it. It has early-stage script characteristics and may need cleanup or bug fixes before reuse in a larger pipeline.

## Preferred Agent Behavior for This Repo

When making changes:
- prefer surgical edits over broad rewrites
- preserve the local-first workflow unless explicitly asked to add cloud infrastructure
- align new work with the medallion architecture described in `full-spec.md`
- keep documentation synchronized with actual commands and folder structure
- do not invent CI, deployment, or production services that do not exist in the repo yet

If adding new project areas, update this file so future agents have accurate instructions.
