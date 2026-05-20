---
tags: [mlops, spec, nyc-taxi, airflow, mlflow, dbt, duckdb, dvc]
type: guide
domain: mlops
date: 2026-05-19
relates: ["[[lesson-1]]", "[[monorepo-decision]]", "[[full-spec]]"]
---

# Full spec: NYC taxi MLOps monorepo

## Quick summary

This note is the full working spec for the project.

It defines:

- what the project is
- what the monorepo should contain
- what order the work should happen in
- why `DAGs` and `dbt` should not be written first
- what the first code files should do
- what counts as done for each early milestone

This is a planning and execution spec for a local-first MLOps lab, not a generic tutorial.

## Project description

Build a local-first, end-to-end MLOps system around the NYC taxi dataset.

The system should simulate a realistic batch ML lifecycle:

```text
web data
    -> bronze
    -> silver
    -> gold
    -> training
    -> experiment tracking
    -> model registry
    -> batch scoring
    -> monitoring
    -> retraining decision
    -> orchestration
```

The core prediction task is:

- predict `trip_duration_minutes`

The project is meant to demonstrate:

- medallion-style data design
- reproducible ML workflows
- time-aware evaluation
- model registry workflows
- batch scoring
- drift and performance monitoring
- retraining lifecycle thinking

## Primary learning goals

The project should teach the parts of MLOps that are usually missing from basic ML projects:

- how raw data becomes a model-ready dataset
- how model training becomes reproducible
- how model runs, artifacts, and parameters are tracked
- how a candidate model becomes a production model
- how production predictions are monitored over time
- how a retraining decision is made using data, not guesswork

## What this project is not

This project is not primarily about:

- real-time streaming
- Kubernetes
- distributed object storage
- advanced infrastructure automation
- training a state-of-the-art model
- data warehouse ingestion as the main learning goal

Those topics are explicitly out of scope for version 1.

## Final monorepo decision

This project should be a single monorepo.

Reason:

- the system is one connected lifecycle
- the data, feature, training, orchestration, and monitoring layers are tightly coupled
- one repo is easier to run locally
- one repo is easier to understand as a portfolio project
- splitting repos now would add process overhead without increasing learning value

## Planned stack

| Concern | Tool |
|---|---|
| Python environment | `uv` |
| Raw and transformed data | local parquet files |
| SQL transformation layer | `dbt` |
| Local analytical engine | `DuckDB` |
| Data artifact versioning | `DVC` |
| Experiment tracking and registry | `MLflow` |
| Workflow orchestration | `Apache Airflow` |
| Monitoring | `Evidently` |
| Metadata / serving tables | `PostgreSQL` |
| Local services | `Docker Compose` |

## Repo structure spec

This is the target monorepo structure.

```text
nyc-taxi-mlops/
├── .dvc/
├── .gitignore
├── dvc.yaml
├── pyproject.toml
├── uv.lock
├── README.md
├── docker-compose.yml
├── airflow/
│   └── dags/
│       ├── data_pipeline.py
│       └── ml_pipeline.py
├── data/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── monitoring/
├── dbt_taxi/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── bronze/
│   │   ├── silver/
│   │   └── gold/
│   ├── tests/
│   └── macros/
├── notebooks/
│   └── 01_data_exploration.ipynb
├── reports/
│   └── evidently/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data/
│   │   └── io.py
│   ├── ingest/
│   │   └── fetch_taxi_data.py
│   ├── ml/
│   │   ├── train.py
│   │   ├── score.py
│   │   └── registry.py
│   └── monitor/
│       └── evaluate_drift.py
└── tests/
    ├── dags/
    ├── src/
    └── test_data_contracts.py
```

## Boundary rules

These boundaries are mandatory because they keep the monorepo understandable.

### Airflow responsibility

`Airflow` should only orchestrate.

Allowed in DAG files:

- task definitions
- dependencies
- scheduling
- retries
- handoff between steps

Not allowed in DAG files:

- large SQL transformations
- full model training logic
- feature engineering logic
- notebook-style exploratory code

Rule:

- DAGs call reusable code in `src/` or `dbt`

### dbt responsibility

`dbt_taxi/` should own transformation logic.

Allowed in dbt:

- bronze staging views or tables
- silver cleaning logic
- gold feature tables
- data tests
- documentation and macros

Not allowed in dbt:

- model training
- MLflow logging
- registry logic
- monitoring logic

### src responsibility

`src/` should own reusable Python logic.

Examples:

- pulling data from the web
- loading and saving files
- model training scripts
- model scoring scripts
- monitoring scripts
- registry promotion logic

### notebooks responsibility

`notebooks/` should stay exploratory.

Notebook code is allowed to:

- inspect schema
- explore target distributions
- check nulls and outliers
- test quick feature ideas
- validate that the task is worth formalizing

Notebook code should not be treated as production code.

If a notebook step becomes necessary for the real pipeline, it must be rewritten into `src/` or `dbt`.

## Why the first code is not DAGs or dbt

This is the most important sequencing rule in the project.

Do not start by writing `Airflow DAGs`.

Do not start by writing `dbt silver/gold models`.

### Why not DAGs first

Airflow is for orchestrating known workflow steps.

At the beginning of the project, these details are not known yet:

- exact raw schema
- actual timestamp columns
- real null patterns
- cleaning rules
- target definition details
- useful feature columns
- correct train and validation windows
- realistic failure conditions

If DAGs are written before those facts are discovered, the DAG structure will likely be wrong.

Typical mistakes from writing DAGs too early:

- wrong task boundaries
- wrong assumptions about inputs and outputs
- wrong validation points
- wrong schedules
- wrong retraining trigger logic

Airflow should formalize a workflow after the workflow is understood.

### Why not dbt first

dbt silver and gold models encode assumptions about:

- source column names
- valid business rules
- invalid records
- target derivation
- feature definitions

At the start, these are still unknown.

If dbt models are written first, they are mostly guesses.

Typical mistakes from writing dbt too early:

- filtering the wrong rows
- choosing the wrong timestamp field
- building a gold table before the target is validated
- encoding feature logic that later has to be thrown away

dbt should formalize data rules after the rules are discovered from real data.

## Correct execution order

This is the intended order of work.

### Phase 0: repo and environment setup

Goal:

- create the project shell

Outputs:

- GitHub repo exists
- `uv` is initialized
- base folders exist
- `README.md` exists

### Phase 1: raw data acquisition and exploration

Goal:

- get real data into bronze
- understand the data before formalizing transformations

Outputs:

- `src/ingest/fetch_taxi_data.py`
- one raw parquet file in `data/bronze/`
- `notebooks/01_data_exploration.ipynb`
- validated target definition

### Phase 2: formalize data rules with dbt

Goal:

- convert notebook findings into silver and gold transformations

Outputs:

- `dbt_taxi` project
- silver cleaning models
- gold feature model
- dbt tests for key assumptions

### Phase 3: model training and MLflow

Goal:

- make training reproducible

Outputs:

- `src/ml/train.py`
- tracked experiments in MLflow
- registered candidate model

### Phase 4: batch scoring and monitoring

Goal:

- simulate production behavior

Outputs:

- `src/ml/score.py`
- `src/monitor/evaluate_drift.py`
- prediction outputs
- monitoring report

### Phase 5: orchestration with Airflow

Goal:

- automate known lifecycle steps

Outputs:

- training DAG
- scoring DAG
- monitoring DAG

## The first files to create

These are the first concrete files that should be written.

### 1. `README.md`

Purpose:

- define the project clearly before implementation spreads

Must contain:

- one-paragraph project summary
- target prediction task
- planned stack
- planned lifecycle
- target repo structure
- current implementation status

Why first:

- it locks the project scope
- it prevents drift in architecture decisions
- it gives a future OpenCode session a high-signal summary immediately

### 2. `src/ingest/fetch_taxi_data.py`

Purpose:

- download raw data from the source and create the bronze layer

Must do:

- accept or define a source URL for a monthly taxi parquet file
- create `data/bronze/` if it does not exist
- download one file only at first
- save the file exactly as raw source data
- skip work if the file already exists or provide a safe overwrite option later

Must not do:

- cleaning
- schema normalization
- target derivation
- feature engineering

Why first:

- no downstream work matters until raw data is available
- it creates the first durable artifact in the pipeline
- it confirms the source is accessible and usable

### 3. `notebooks/01_data_exploration.ipynb`

Purpose:

- inspect the real raw data and discover the rules the pipeline must encode

Must cover:

- dataset shape
- columns and types
- null counts
- target creation for `trip_duration_minutes`
- distribution of trip duration
- obvious outliers
- time-aware exploratory checks
- candidate feature columns

Must answer these questions:

- which columns exist and matter?
- how exactly should `trip_duration_minutes` be defined?
- which rows should be considered invalid?
- which temporal split will represent production behavior?
- which features should be included in the first gold dataset?

Why third:

- this notebook is where assumptions become evidence
- the silver and gold design should come from this notebook

## Detailed spec for the first script

File:

- `src/ingest/fetch_taxi_data.py`

### Functional requirements

The script should:

1. define a source URL for one monthly NYC taxi parquet file
2. define an output path under `data/bronze/`
3. create parent directories if they do not exist
4. fetch the file from the web
5. write the raw bytes to disk without modification
6. print or log the final saved path

### Non-functional requirements

The script should be:

- simple
- rerunnable
- safe for local use
- free of transformation logic

### Acceptance criteria

The script is complete when:

- running it creates a parquet file in `data/bronze/`
- the file opens successfully in the notebook
- the filename clearly indicates the month or source file

## Detailed spec for the first notebook

File:

- `notebooks/01_data_exploration.ipynb`

### Required sections

#### Section 1: load raw data

Must:

- load the bronze parquet file
- display shape
- preview a sample

#### Section 2: inspect schema

Must:

- list columns
- inspect data types
- identify likely target-related and time-related columns

#### Section 3: define target

Must:

- derive `trip_duration_minutes`
- explain exactly which timestamp columns were used
- inspect descriptive statistics

#### Section 4: validate target quality

Must:

- identify negative durations
- identify zero-duration records
- identify extreme outliers
- decide a first-pass validity rule

#### Section 5: inspect missingness

Must:

- count nulls per relevant column
- identify which columns are unreliable

#### Section 6: time behavior

Must:

- inspect pickup hour patterns
- inspect weekday patterns
- look for temporal variation that justifies time-based splitting

#### Section 7: first feature candidates

Must:

- list candidate features for gold
- identify any columns that might cause leakage

#### Section 8: conclusions

Must produce a short written summary of:

- target definition
- initial cleaning rules
- likely feature list
- proposed time split

### Acceptance criteria

The notebook is complete when it gives enough evidence to write:

- silver cleaning logic
- gold feature logic
- the first training split strategy

## What silver should probably formalize later

Only after the notebook is complete should silver models be created.

The silver layer will likely contain rules such as:

- drop rows with missing pickup or dropoff timestamps
- drop rows with non-positive trip distance
- drop rows with impossible or negative duration
- standardize timestamp names
- preserve raw identifiers needed for features

These are examples, not final rules, until confirmed in the notebook.

## What gold should probably formalize later

Only after the notebook is complete should gold models be created.

The gold layer will likely contain:

- trip distance
- passenger count
- pickup hour
- pickup day of week
- weekend flag
- rush hour flag
- pickup location id
- dropoff location id
- target column `trip_duration_minutes`

Again, the exact set must come from real exploration, not assumption.

## What the first Airflow DAGs should look like later

Airflow comes after data and training logic exist.

### Training DAG

```text
fetch_raw_data
    -> build_silver_gold
    -> train_candidate_model
    -> evaluate_candidate_model
    -> register_candidate_model
```

### Batch scoring DAG

```text
load_production_model
    -> load_gold_scoring_data
    -> score_predictions
    -> store_predictions
```

### Monitoring DAG

```text
load_reference_window
    -> load_current_window
    -> calculate_metrics
    -> detect_drift
    -> decide_retraining
```

These DAGs should only be created after each task is already runnable outside Airflow.

## Day 1 implementation checklist

This is the first practical checkpoint.

By the end of the first session, you should have:

- created the repo
- initialized `uv`
- created the folder structure
- written `README.md`
- written `src/ingest/fetch_taxi_data.py`
- downloaded one parquet file into `data/bronze/`
- created `notebooks/01_data_exploration.ipynb`
- verified the target is feasible

If these are not complete, do not move on to dbt or Airflow.

## Stop conditions

Stop and revise the plan if any of these happen during exploration:

- the chosen parquet file has unexpected schema issues
- the timestamp fields are not what the project assumed
- the target cannot be derived cleanly
- the data quality is much worse than expected
- the planned feature set depends on unavailable columns

If one of these happens, update this spec before building downstream layers.

## Definition of ready for dbt

You are ready to write silver and gold models only when you can answer all of these clearly:

1. What is the exact raw schema being used?
2. How is `trip_duration_minutes` defined?
3. Which rows are invalid and must be removed?
4. Which columns are needed for the first model?
5. What should the training time split be?

If any of these are still uncertain, dbt is premature.

## Definition of ready for Airflow

You are ready to write DAGs only when you already have runnable commands or scripts for:

1. fetch raw data
2. build silver and gold
3. train the model
4. score a batch
5. generate monitoring outputs

If those steps do not work manually, Airflow should not be added yet.

## Final recommendation

Start with the smallest real step that produces durable project truth:

- pull one raw parquet file
- inspect it in a notebook
- use that evidence to define data rules

That is why the first code is the ingestion script, not `dbt` and not `Airflow`.

## Graph View Compatibility Check

- Contains frontmatter with required properties.
- Uses stable headings for future note linking.
- Links to `[[lesson-1]]` and `[[monorepo-decision]]`.
