# DATABASE SCHEMA

# Pit Wall Insight

Version: 1.0

Status: Planning

---

# Overview

Pit Wall Insight follows a dimensional warehouse architecture designed for analytical workloads.

The database is optimized for:

- Fast aggregations
- Historical analysis
- Data consistency
- Read-heavy queries
- Dashboard performance
- Future machine learning features

The warehouse follows a Star Schema.

---

# Database Philosophy

Every table belongs to one of three categories.

```
Raw

↓

Staging

↓

Analytics
```

Only Analytics tables are queried by the backend.

Raw and Staging exist for reproducibility.

---

# Database Layers

## Bronze

Raw immutable data.

Prefix

```
raw_
```

---

## Silver

Validated and normalized data.

Prefix

```
stg_
```

---

## Gold

Business-ready analytical models.

Prefixes

```
dim_

fct_

mart_
```

---

# Entity Relationship Overview

```text
                    dim_season
                         │
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
      ▼                  ▼                  ▼
 dim_driver        dim_constructor      dim_circuit
      │                  │                  │
      └──────────────┬───┴──────────────┐
                     ▼                  ▼
                 dim_session       dim_weather
                     │
                     ▼
                 fct_laps
                     │
     ┌───────────────┼──────────────┐
     ▼               ▼              ▼
fct_telemetry   fct_pitstop   fct_strategy
                     │
                     ▼
              mart_driver_summary
                     │
                     ▼
            mart_constructor_summary
                     │
                     ▼
                mart_dashboard
```

---

# Dimension Tables

Dimension tables contain descriptive information.

---

## dim_driver

Primary Key

```
driver_id
```

Columns

```
driver_number

full_name

abbreviation

nationality

date_of_birth

team_id

rookie_season

world_titles

active

created_at

updated_at
```

Relationships

```
1 Driver

↓

Many Laps

↓

Many Pit Stops

↓

Many Telemetry Records
```

---

## dim_constructor

Primary Key

```
constructor_id
```

Columns

```
team_name

base_country

team_principal

power_unit

primary_color

secondary_color

logo

car_image

active

created_at

updated_at
```

Purpose

Provides UI theming.

---

## dim_circuit

Primary Key

```
circuit_id
```

Columns

```
name

country

city

length

corners

drs_zones

lap_record

clockwise

latitude

longitude

svg_track

created_at
```

---

## dim_season

Primary Key

```
season_id
```

Columns

```
year

race_count

sprint_count

champion_driver

champion_constructor

created_at
```

---

## dim_session

Primary Key

```
session_id
```

Columns

```
season_id

race_name

session_type

date

weather_id

circuit_id
```

Session Types

```
FP1

FP2

FP3

Sprint Shootout

Sprint

Qualifying

Race
```

---

## dim_weather

Primary Key

```
weather_id
```

Columns

```
air_temperature

track_temperature

humidity

wind_speed

wind_direction

rainfall

pressure

track_status
```

---

# Fact Tables

Fact tables contain measurable events.

---

## fct_laps

Grain

One record

=

One Driver

+

One Lap

Primary Key

```
lap_id
```

Columns

```
driver_id

session_id

lap_number

lap_time

sector_1

sector_2

sector_3

compound

tyre_life

position

speed_trap

drs

pit_in

pit_out

created_at
```

---

## fct_telemetry

Grain

One telemetry sample.

Columns

```
driver_id

session_id

lap_number

timestamp

speed

rpm

gear

throttle

brake

drs

x

y

z
```

Future

100ms sampling.

---

## fct_pitstop

Columns

```
pitstop_id

driver_id

session_id

lap

pit_duration

stop_number

compound_before

compound_after

created_at
```

---

## fct_strategy

Stores stint-level analytics.

Columns

```
strategy_id

driver_id

session_id

stint

compound

laps

average_pace

pit_loss

position_change
```

---

## fct_results

Columns

```
result_id

driver_id

session_id

grid_position

finish_position

points

status

fastest_lap

laps_completed
```

---

# Mart Tables

Mart tables serve the frontend.

---

## mart_dashboard

Contains

Season KPIs.

Columns

```
season

drivers

constructors

races

fastest_pitstop

average_overtakes

fastest_lap

championship_gap
```

---

## mart_driver_summary

Contains

Driver statistics.

Columns

```
driver

wins

podiums

poles

fastest_laps

average_finish

average_qualifying

consistency_score

pit_efficiency

race_pace

qualifying_pace
```

---

## mart_constructor_summary

Contains

Team analytics.

Columns

```
constructor

wins

podiums

pitstop_average

strategy_success

average_points

dnf_rate

development_index

average_pace
```

---

## mart_strategy_analysis

Contains

Race strategy metrics.

Columns

```
driver

race

strategy

pit_window

pit_loss

undercut_gain

overcut_gain

stint_duration

compound
```

---

## mart_race_summary

Contains

Race overview.

Columns

```
race

winner

pole

fastest_lap

average_pitstop

safety_car_laps

red_flags

weather

retirements
```

---

## mart_telemetry_summary

Contains

Engineering metrics.

Columns

```
driver

average_speed

top_speed

average_throttle

average_brake

average_rpm

drs_usage

gear_changes
```

---

# Relationships

```
Driver

1

↓

Many Laps

Many Pit Stops

Many Results

Many Telemetry
```

---

```
Constructor

1

↓

Many Drivers
```

---

```
Circuit

1

↓

Many Sessions
```

---

```
Session

1

↓

Many Laps

Many Results

Many Strategies

Many Telemetry
```

---

# Index Strategy

Indexes should exist on

```
driver_id

constructor_id

session_id

season_id

lap_number

compound

race_name

timestamp
```

Composite Indexes

```
(driver_id, session_id)

(session_id, lap_number)

(driver_id, lap_number)

(constructor_id, season_id)
```

---

# Partition Strategy

Future

Partition

```
Season

↓

Session

↓

Telemetry
```

Large telemetry tables should be partitioned.

---

# Naming Convention

Primary Keys

```
driver_id

lap_id

constructor_id
```

Foreign Keys

```
driver_id

session_id

constructor_id
```

Dates

```
created_at

updated_at
```

Booleans

```
is_

has_

can_
```

Consistency is mandatory.

---

# Data Types

IDs

UUID

Text

VARCHAR

Large Text

TEXT

Numbers

INTEGER

Timing

INTERVAL

Telemetry

DOUBLE PRECISION

Booleans

BOOLEAN

Dates

TIMESTAMP WITH TIME ZONE

---

# Data Integrity

Every table must enforce

Primary Keys

Foreign Keys

Unique Constraints

Not Null Constraints

Accepted Value Constraints

Relationship Tests

---

# Soft Deletes

No analytical table should use soft deletes.

Historical records remain permanently available.

---

# Audit Fields

Every table includes

```
created_at

updated_at

pipeline_version

source
```

Supports

- lineage
- debugging
- reproducibility

---

# Future Tables

```
fct_live_telemetry

fct_weather_stream

fct_predictions

dim_tyre

dim_engine

mart_driver_predictions

mart_strategy_predictions
```

Architecture should support these additions.

---

# Engineering Decisions

## Decision 001

Star Schema

Status

✅ Accepted

Reason

Optimized for analytical workloads and BI queries.

---

## Decision 002

UUID Primary Keys

Status

✅ Accepted

Reason

Globally unique identifiers improve scalability and future distributed systems support.

---

## Decision 003

Analytics Marts

Status

✅ Accepted

Reason

Frontend consumes curated analytical models rather than raw operational tables.

---

## Decision 004

Immutable Historical Records

Status

✅ Accepted

Reason

Preserves reproducibility and historical accuracy.

---

## Decision 005

Telemetry Separation

Status

✅ Accepted

Reason

Telemetry data grows rapidly and should remain isolated from traditional analytical facts.

---

# Definition of Done

The database schema is complete when

✓ Every entity has a defined purpose

✓ Relationships are normalized

✓ Fact and dimension tables follow a star schema

✓ Analytical marts support frontend requirements

✓ Indexes exist for high-frequency queries

✓ Constraints enforce data integrity

✓ Audit fields enable reproducibility

✓ Future telemetry expansion is supported

✓ Documentation remains synchronized with implementation