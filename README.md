# nyc-taxi-mlops

Local-first NYC taxi MLOps lab built around parquet files, `DuckDB`, and `dbt`.

## Overview

This repository is an early-stage monorepo for learning and demonstrating an end-to-end batch ML workflow on NYC taxi trip data.

Current scope:

- ingest raw NYC taxi parquet files into a local bronze layer
- transform raw data with `dbt` + `DuckDB`
- formalize data quality and feature rules from notebook exploration
- evolve toward a medallion-style ML workflow

Primary prediction target:

- `trip_duration_minutes`

## Current Stack

- Python `3.12+`
- `uv` for dependency and environment management
- `dbt-duckdb`
- DuckDB
- Jupyter notebooks for exploration
- local parquet files for raw data artifacts

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

## Quick Start

### 1. Install dependencies

```bash
uv sync
```

### 2. Download sample raw data

```bash
uv run python src/ingest/fetch_taxi_data.py --taxi-type yellow --year 2026 --month 1
```

Downloaded parquet files are stored under `data/bronze/`.

### 3. Run dbt models

```bash
cd dbt_taxi
dbt build
```

## Data Ingestion

Current ingestion entrypoint:

- `src/ingest/fetch_taxi_data.py`

Example commands:

```bash
uv run python src/ingest/fetch_taxi_data.py --taxi-type yellow --year 2026 --month 1
uv run python src/ingest/fetch_taxi_data.py --taxi-type yellow --year 2026 --month 1 --overwrite
```

Supported taxi types today:

- `yellow`
- `green`

## dbt Workflow

Run dbt commands from `dbt_taxi/`.

Common commands:

```bash
cd dbt_taxi
dbt parse
dbt run
dbt test
dbt build
dbt seed
dbt clean
```

Current model materializations:

- `bronze`: `view`
- `silver`: `view`
- `gold`: `table`

## Modeling Rules

Current rules derived from `phase-1-outcomes.md`:

### Target

- predict `trip_duration_minutes`
- derive it from `tpep_dropoff_datetime - tpep_pickup_datetime`

### First-pass cleaning

- require non-null pickup and dropoff timestamps
- require positive trip duration
- require positive trip distance
- remove negative `fare_amount` and `total_amount`
- cap initial trip duration at 180 minutes
- cap initial trip distance at 50 miles

### Leakage constraints

Do not use post-trip outcome fields as pickup-time features, including:

- `tpep_dropoff_datetime`
- `trip_duration_minutes`

### Train / validation / test policy

- use chronological splits
- do not use random splits for the initial workflow

## Development Notes

- `src/` owns reusable Python logic
- `dbt_taxi/` owns SQL transformations and data tests
- `notebooks/` is exploratory only
- if notebook logic becomes repeatable, move it into `src/` or `dbt_taxi/`

## Validation

This project is still early-stage and does not yet have a broad Python test suite.

Current validation methods:

- run ingestion scripts directly with `uv run python ...`
- run `dbt build` or `dbt test` from `dbt_taxi/`
- verify assumptions against `phase-1-outcomes.md`

## Related Docs

- `full-spec.md` — working project specification and roadmap
- `phase-1-outcomes.md` — target, cleaning, and feature decisions from notebook exploration
- `AGENTS.md` — agent-focused implementation guidance for this repository

## Git Hygiene

Do not commit local generated artifacts such as:

- `data/`
- `logs/`
- `.venv/`
- `__pycache__/`
- local DuckDB files
