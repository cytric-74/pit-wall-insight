# API SPECIFICATION

# Pit Wall Insight

Version: 1.0

Status: Planning

---

# Overview

The Pit Wall Insight API exposes analytical Formula One data through a clean, versioned, RESTful interface.

The API is designed around resources instead of database tables.

Endpoints should answer analytical questions rather than exposing raw data.

The API acts as the only communication layer between the frontend and the analytics warehouse.

Frontend applications must never communicate directly with PostgreSQL.

---

# Design Principles

The API should be

- RESTful
- Predictable
- Typed
- Versioned
- Cache Friendly
- Fast
- Self Documenting

Every endpoint should represent a business capability.

Not a database query.

---

# Base URL

Development

```
http://localhost:8000/api/v1
```

Production

```
https://api.pitwallinsight.com/api/v1
```

---

# API Versioning

Current Version

```
v1
```

Future

```
v2

v3
```

Breaking changes require a new version.

---

# Authentication

Version 1

Public Read API

Future

JWT Authentication

OAuth

Role Based Permissions

API Keys

---

# Standard Response

Successful Response

```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "",
    "execution_time": "42ms"
  }
}
```

---

Collection Response

```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 25,
    "total": 340,
    "pages": 14
  }
}
```

---

Error Response

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Driver not found."
  },
  "request_id": ""
}
```

---

# Endpoint Categories

```
Dashboard

Drivers

Constructors

Races

Sessions

Telemetry

Strategy

Circuits

Seasons

Comparison

Search

Health
```

---

# Dashboard

## GET

```
/dashboard
```

Returns

- Championship overview
- Driver standings
- Constructor standings
- Recent races
- Fastest lap
- Average pit stop
- Overtakes
- Championship gap

---

## GET

```
/dashboard/highlights
```

Returns

Weekly highlights.

---

# Drivers

## GET

```
/drivers
```

Returns

Driver list.

Supports

```
season

constructor

nationality

active

page

limit

sort
```

---

## GET

```
/drivers/{driverId}
```

Returns

Driver profile.

---

## GET

```
/drivers/{driverId}/statistics
```

Returns

Career statistics.

---

## GET

```
/drivers/{driverId}/laps
```

Supports

```
season

race

session

compound
```

Returns

Lap data.

---

## GET

```
/drivers/{driverId}/telemetry
```

Returns

Telemetry traces.

---

## GET

```
/drivers/{driverId}/consistency
```

Returns

Consistency metrics.

---

## GET

```
/drivers/{driverId}/comparison/{otherDriverId}
```

Returns

Driver comparison.

---

# Constructors

## GET

```
/constructors
```

Returns

Constructor list.

---

## GET

```
/constructors/{constructorId}
```

Returns

Constructor profile.

---

## GET

```
/constructors/{constructorId}/drivers
```

Returns

Current drivers.

---

## GET

```
/constructors/{constructorId}/statistics
```

Returns

Team analytics.

---

## GET

```
/constructors/{constructorId}/strategy
```

Returns

Strategy overview.

---

## GET

```
/constructors/{constructorId}/performance
```

Returns

Performance trends.

---

# Seasons

## GET

```
/seasons
```

Returns

Available seasons.

---

## GET

```
/seasons/{season}
```

Returns

Season summary.

---

## GET

```
/seasons/{season}/standings
```

Returns

Championship standings.

---

## GET

```
/seasons/{season}/calendar
```

Returns

Race calendar.

---

# Races

## GET

```
/races
```

Returns

Race list.

Supports

```
season

country

page

limit
```

---

## GET

```
/races/{raceId}
```

Returns

Race summary.

---

## GET

```
/races/{raceId}/timeline
```

Returns

Race events.

---

## GET

```
/races/{raceId}/positions
```

Returns

Position changes.

---

## GET

```
/races/{raceId}/pitstops
```

Returns

Pit stop timeline.

---

## GET

```
/races/{raceId}/weather
```

Returns

Weather evolution.

---

## GET

```
/races/{raceId}/strategy
```

Returns

Strategy overview.

---

## GET

```
/races/{raceId}/replay
```

Returns

Replay timeline.

---

# Sessions

## GET

```
/sessions/{sessionId}
```

Returns

Session metadata.

---

## GET

```
/sessions/{sessionId}/results
```

Returns

Session results.

---

## GET

```
/sessions/{sessionId}/laps
```

Returns

Lap table.

---

# Telemetry

## GET

```
/telemetry
```

Supports

```
driver

lap

session

```

---

## GET

```
/telemetry/speed
```

Returns

Speed trace.

---

## GET

```
/telemetry/throttle
```

Returns

Throttle trace.

---

## GET

```
/telemetry/brake
```

Returns

Brake trace.

---

## GET

```
/telemetry/gear
```

Returns

Gear changes.

---

## GET

```
/telemetry/drs
```

Returns

DRS usage.

---

## GET

```
/telemetry/corner-analysis
```

Returns

Corner-by-corner comparison.

---

# Strategy

## GET

```
/strategy
```

Returns

Season strategies.

---

## GET

```
/strategy/undercut
```

Returns

Undercut analysis.

---

## GET

```
/strategy/overcut
```

Returns

Overcut analysis.

---

## GET

```
/strategy/tyres
```

Returns

Tyre degradation.

---

## GET

```
/strategy/simulation
```

Returns

Strategy simulation.

Future

POST

Simulation scenarios.

---

# Circuits

## GET

```
/circuits
```

Returns

Circuit list.

---

## GET

```
/circuits/{circuitId}
```

Returns

Circuit details.

---

## GET

```
/circuits/{circuitId}/history
```

Returns

Historical results.

---

## GET

```
/circuits/{circuitId}/records
```

Returns

Track records.

---

# Comparison

## GET

```
/compare/drivers
```

Supports

```
driverA

driverB
```

---

## GET

```
/compare/constructors
```

Returns

Constructor comparison.

---

## GET

```
/compare/races
```

Returns

Race comparison.

---

# Search

## GET

```
/search
```

Supports

```
query
```

Returns

Drivers

Constructors

Circuits

Races

Seasons

---

# Health

## GET

```
/health
```

Returns

Application health.

---

## GET

```
/ready
```

Returns

Readiness probe.

---

## GET

```
/live
```

Returns

Liveness probe.

---

# Query Parameters

Pagination

```
page

limit
```

Sorting

```
sort

order
```

Filtering

```
season

race

driver

constructor

session

compound

country
```

Search

```
query
```

---

# Status Codes

```
200 OK

201 Created

204 No Content

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Validation Error

429 Too Many Requests

500 Internal Server Error
```

---

# Caching

Client

TanStack Query

↓

Backend

ETag

↓

Future

Redis

Endpoints suitable for caching

- standings
- circuits
- constructors
- historical races

Telemetry endpoints should bypass cache when live mode is introduced.

---

# Rate Limiting

Future

Anonymous

100 requests/minute

Authenticated

1000 requests/minute

---

# OpenAPI

Generated automatically.

Available at

```
/docs
```

Redoc

```
/redoc
```

No manual API documentation should be maintained.

---

# API Design Rules

Never

❌ Expose database table names

❌ Return SQLAlchemy models

❌ Return inconsistent response structures

❌ Return snake_case to frontend

Always

✅ Return typed DTOs

✅ Use camelCase responses

✅ Validate every request

✅ Keep endpoint responsibilities focused

✅ Maintain backwards compatibility within a version

---

# Future API Features

- GraphQL Gateway
- WebSocket Live Telemetry
- Server Sent Events
- AI Insights Endpoint
- Race Prediction API
- Export API
- Report Generation API
- Public Developer API

---

# Engineering Decisions

## Decision 001

REST API First

Status

✅ Accepted

Reason

Simple, predictable, well supported, and ideal for frontend consumption.

---

## Decision 002

Versioned API

Status

✅ Accepted

Reason

Supports future evolution without breaking existing clients.

---

## Decision 003

Business-Oriented Endpoints

Status

✅ Accepted

Reason

Endpoints should expose analytical capabilities rather than database entities.

---

## Decision 004

Consistent Response Contract

Status

✅ Accepted

Reason

Simplifies frontend development and improves error handling.

---

## Decision 005

Typed DTO Responses

Status

✅ Accepted

Reason

Ensures strong contracts between backend and frontend.

---

# Definition of Done

The API specification is complete when

✓ Every frontend feature has a corresponding endpoint

✓ All endpoints are versioned

✓ Request and response formats are standardized

✓ Validation rules are documented

✓ Error handling is consistent

✓ OpenAPI documentation is generated automatically

✓ Endpoint responsibilities remain focused

✓ Future API evolution can occur without breaking existing clients