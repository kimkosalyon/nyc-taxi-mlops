# Phase 1 Outcomes

This document captures the current Phase 1 decisions derived from the raw bronze-layer NYC taxi data exploration in `notebooks/01_data_exploration.ipynb`.

## 1. Target definition

**Target column:** `trip_duration_minutes`

**Definition:**

- derive the target from raw trip timestamps
- use `tpep_pickup_datetime` as trip start
- use `tpep_dropoff_datetime` as trip end
- compute:

$$
\text{trip\_duration\_minutes} = \frac{\text{tpep\_dropoff\_datetime} - \text{tpep\_pickup\_datetime}}{60 \text{ seconds}}
$$

**Implementation rule:**

- create `trip_duration_minutes` from the timestamp difference in minutes
- treat this as the prediction target, not an input feature

**Modeling note:**

If the prediction task is trip duration **at pickup time**, then any post-trip information must be excluded from features.

## 2. Initial cleaning rules

These rules should become the first-pass silver-layer data quality filters.

### Required timestamp validity

- drop rows where `tpep_pickup_datetime` is null
- drop rows where `tpep_dropoff_datetime` is null
- drop rows where `trip_duration_minutes <= 0`

### Target outlier rule

For initial modeling and EDA, keep only trips with:

- `trip_duration_minutes > 0`
- `trip_duration_minutes <= 180`

This creates a practical first-pass cap of 3 hours and removes clearly unrealistic or highly noisy trips from the first model iteration.

### Distance validity

- drop rows where `trip_distance <= 0`
- for initial modeling, keep only rows with `trip_distance <= 50`

### Fare and total amount validity

- drop rows where `fare_amount < 0`
- drop rows where `total_amount < 0`

### Duplicate and anomalous records

The notebook checks for:

- duplicate rows
- zero distance with positive fare
- zero duration with positive distance

These should be monitored and reviewed during silver modeling. For the first pass, clearly invalid duration and distance rules are the main enforced filters.

## 3. First feature set

These are the safest first-pass candidate features based on the current notebook work.

### Primary feature candidates

- `pickup_hour`
- `pickup_weekday`
- `is_weekend`
- `trip_distance`
- `passenger_count`
- `PULocationID`
- `DOLocationID` *(only if destination is known at prediction time)*

### Derived features already supported by the notebook

- `pickup_hour` from `tpep_pickup_datetime`
- `pickup_weekday` from `tpep_pickup_datetime`
- `pickup_date` for temporal analysis and splitting
- `is_weekend` from pickup weekday

### Leakage exclusions

Do **not** use the following as model inputs for a pickup-time prediction task:

- `tpep_dropoff_datetime`
- `trip_duration_minutes`
- any post-trip outcome field only known after ride completion

## 4. Time-based split strategy

The split should reflect real production behavior, so it must be chronological rather than random.

### Recommended strategy

- sort data by `tpep_pickup_datetime`
- train on earlier trips
- validate on later trips
- test on the most recent held-out time window

### Initial practical split

If working with multiple months of bronze data:

- **train:** earliest available period
- **validation:** next chronological period
- **test:** most recent chronological period

### Example policy

For a small local-first setup using monthly files:

- train on older month(s)
- validate on the next month or late slice of the training range
- test on the latest month

### Why this strategy

A time-based split is required because:

- trip behavior varies by hour, weekday, and date
- random splits would leak future behavior into training
- the project goal is to simulate batch production prediction, not IID offline benchmarking

## Summary

### Target

- predict `trip_duration_minutes`
- derive it from `tpep_dropoff_datetime - tpep_pickup_datetime`

### Initial silver rules

- require non-null pickup and dropoff timestamps
- require positive trip duration
- require positive trip distance
- remove negative monetary values
- cap duration and distance for the first-pass model dataset

### First feature set

- pickup-time temporal features
- trip distance
- passenger count
- pickup and dropoff location IDs, subject to prediction-time availability

### Split policy

- use chronological train/validation/test splits based on pickup timestamp
- never use a random split for the initial production-style workflow

## Status

These outcomes are sufficient to start formalizing:

- silver cleaning logic
- the first gold feature dataset
- the first reproducible training split design

They should still be revised if later exploration reveals schema changes, stronger outlier rules, or unavailable prediction-time features.
