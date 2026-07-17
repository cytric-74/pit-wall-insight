# DATA ENGINEERING ARCHITECTURE

# Pit Wall Insight

Version: 1.0

Status: Planning

---

# Overview

The Data Engineering layer is responsible for collecting, validating, transforming, and modeling Formula One data into reliable analytical datasets.

The objective is to create an automated, scalable, and reproducible pipeline that transforms raw telemetry and race information into business-ready analytics.

Every dataset should be reproducible.

Every transformation should be documented.

Every metric should be traceable back to its source.

---

# Goals

The pipeline should

- Collect Formula One data automatically
- Validate incoming datasets
- Store immutable raw data
- Transform data using dbt
- Build analytics-ready tables
- Refresh after every race weekend
- Be fully reproducible
- Scale to future seasons

---

# Data Pipeline Overview

```text
                    FastF1 API
                       │
                       ▼
             Python Data Collectors
                       │
                       ▼
              Validation Pipeline
                       │
                       ▼
          PostgreSQL Bronze Layer
                       │
                       ▼
               dbt Staging Models
                       │
                       ▼
           dbt Intermediate Models
                       │
                       ▼
              dbt Analytics Marts
                       │
                       ▼
         FastAPI Analytics Services
                       │
                       ▼
            React Analytics Platform
```

---

# Data Sources

Primary

FastF1 API

Provides

- Sessions
- Lap Times
- Telemetry
- Weather
- Tyres
- Pit Stops
- Drivers
- Constructors

---

Secondary

Ergast API

Provides

- Historical Results
- Driver Standings
- Constructor Standings
- Race Calendar

---

Future Sources

OpenF1

AWS Open Data

Official FIA Documents

Weather APIs

Circuit Metadata APIs

Telemetry Streaming APIs

---

# Data Architecture

Three logical layers

```
Bronze

↓

Silver

↓

Gold
```

---

# Bronze Layer

Purpose

Store raw immutable data.

Characteristics

- Minimal transformation
- Source aligned
- Append only
- Historical preservation

Tables

```
raw_sessions

raw_laps

raw_weather

raw_drivers

raw_telemetry

raw_pitstops

raw_results

raw_constructors

raw_circuits
```

Nothing is deleted.

---

# Silver Layer

Purpose

Cleaning.

Normalization.

Validation.

Responsibilities

- Standardized naming
- Remove duplicates
- Normalize timestamps
- Data typing
- Missing value handling
- Integrity checks

Models

```
stg_sessions

stg_laps

stg_weather

stg_drivers

stg_results

stg_telemetry

stg_pitstops
```

---

# Gold Layer

Purpose

Analytics.

Business-ready models.

Contains

- Fact Tables
- Dimension Tables
- Aggregated Metrics

Only this layer is consumed by the API.

---

# ETL Pipeline

Extract

↓

Validate

↓

Clean

↓

Normalize

↓

Load Bronze

↓

Transform with dbt

↓

Create Analytics Tables

↓

Serve API

Pipeline must be repeatable.

---

# Folder Structure

```text
apps/ingestion/

├── collectors/
│
├── loaders/
│
├── transformers/
│
├── validators/
│
├── scheduler/
│
├── config/
│
├── logs/
│
├── utils/
│
└── main.py
```

---

# Collectors

Responsible for downloading data.

Example

```
collectors/

fastf1.py

ergast.py

weather.py

circuits.py
```

Collectors never modify data.

---

# Validators

Responsible for

- Missing values
- Schema validation
- Duplicate detection
- Invalid timestamps
- Foreign key validation
- Null checks

Validation failures are logged.

Pipeline should continue where possible.

---

# Loaders

Responsible for

Loading validated datasets into PostgreSQL.

Never perform analytics.

---

# Scheduler

Future automation.

Runs

- Daily refresh
- Race weekend refresh
- Historical sync
- Incremental updates

Initially

GitHub Actions.

Future

Apache Airflow.

---

# Data Refresh Strategy

Historical data

One-time import.

Current season

Refresh after every completed session.

Race Weekend

Practice

↓

Qualifying

↓

Sprint

↓

Race

Every completed session updates analytics.

---

# Incremental Loading

Historical records remain untouched.

Only new sessions are inserted.

Benefits

- Faster refresh
- Lower database load
- Better reproducibility

---

# dbt Project Structure

```text
warehouse/dbt/

models/

staging/

intermediate/

marts/

dimensions/

facts/

snapshots/

tests/

macros/

seeds/

analyses/

docs/
```

---

# Staging Models

Responsibilities

Rename columns

Cast types

Normalize formats

Standardize values

No analytics.

---

# Intermediate Models

Responsibilities

Joins

Relationships

Derived calculations

Reusable transformations

---

# Mart Models

Purpose

Business-ready datasets.

Example

```
mart_driver_performance

mart_constructor_summary

mart_strategy_analysis

mart_race_summary

mart_lap_consistency

mart_pitstop_analysis

mart_telemetry_summary
```

Only marts power the frontend.

---

# Data Quality

Every model should test

- Primary Keys
- Foreign Keys
- Unique IDs
- Accepted Values
- Null Constraints
- Relationships

dbt tests run automatically.

---

# Data Lineage

Every metric should be traceable.

Example

```
Raw Lap

↓

Validated Lap

↓

Driver Performance Model

↓

Driver API

↓

React Dashboard
```

Nothing should become a black box.

---

# Naming Conventions

Raw

```
raw_
```

Staging

```
stg_
```

Intermediate

```
int_
```

Dimensions

```
dim_
```

Facts

```
fct_
```

Analytics

```
mart_
```

Consistency is mandatory.

---

# Metadata

Every table includes

created_at

updated_at

source

season

race_id

pipeline_version

This enables reproducibility.

---

# Data Dictionary

Every table documents

Purpose

Columns

Relationships

Source

Owner

Consumers

Documentation generated through dbt.

---

# Pipeline Monitoring

Log

Pipeline Start

↓

API Calls

↓

Validation

↓

Insert Count

↓

Transform Time

↓

dbt Tests

↓

Pipeline End

Failures should identify the exact stage.

---

# Pipeline Performance

Goals

Historical Import

< 30 minutes

Single Race Refresh

< 3 minutes

Telemetry Refresh

< 60 seconds

dbt Build

< 5 minutes

---

# Future Enhancements

Apache Airflow

Prefect

Kafka

Streaming Telemetry

Redis

Snowflake

BigQuery

DuckDB

Machine Learning Features

Real-Time Event Processing

Architecture should support these additions.

---

# Engineering Standards

Never

❌ Modify raw data

❌ Skip validation

❌ Hardcode transformations

❌ Query bronze tables from the API

Always

✅ Preserve raw data

✅ Validate everything

✅ Build transformations in dbt

✅ Document every model

✅ Version pipelines

---

# Engineering Decisions

## Decision 001

Bronze / Silver / Gold Architecture

Status

✅ Accepted

Reason

Clear separation between ingestion, transformation, and analytics.

---

## Decision 002

dbt

Status

✅ Accepted

Reason

Industry-standard analytics engineering workflow with testing and documentation.

---

## Decision 003

Incremental Loads

Status

✅ Accepted

Reason

Improves refresh performance and reduces unnecessary processing.

---

## Decision 004

Immutable Raw Data

Status

✅ Accepted

Reason

Supports auditing, debugging, and reproducibility.

---

## Decision 005

API Reads Only Gold Models

Status

✅ Accepted

Reason

Keeps analytical queries consistent and optimized.

---

# Definition of Done

The data engineering layer is complete when

✓ Data ingestion is automated

✓ Validation is implemented

✓ Raw data is immutable

✓ dbt models build successfully

✓ Data quality tests pass

✓ Analytics marts are documented

✓ Pipelines are reproducible

✓ Refreshes complete within performance targets

✓ Every metric has documented lineage

✓ The platform can ingest future Formula One seasons without redesign