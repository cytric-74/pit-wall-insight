# BACKEND ARCHITECTURE

# Pit Wall Insight

Version: 1.0

Status: Planning

---

# Overview

The backend is the analytical engine of Pit Wall Insight.

It exists to transform raw Formula One data into meaningful, performant, and reusable analytics.

The backend should expose clean APIs that are completely independent of the frontend implementation.

Business logic must never exist inside API routes.

Every endpoint should remain predictable, testable, and scalable.

---

# Technology Stack

Framework

- FastAPI

Language

- Python 3.12+

ORM

- SQLAlchemy 2.x

Validation

- Pydantic

Database Migration

- Alembic

Authentication (Future)

- JWT
- OAuth2

Caching (Future)

- Redis

Background Tasks

- Celery / FastAPI Background Tasks

Documentation

- OpenAPI
- Swagger

Testing

- Pytest

Containerization

- Docker

---

# Backend Philosophy

The backend should be

- Stateless
- Modular
- Predictable
- Highly Typed
- API First
- Production Ready

Every module should have one responsibility.

---

# Directory Structure

```text
apps/backend/

app/

├── api/
│
├── core/
│
├── database/
│
├── dependencies/
│
├── middleware/
│
├── models/
│
├── repositories/
│
├── schemas/
│
├── services/
│
├── utils/
│
├── exceptions/
│
├── config/
│
└── main.py

tests/

alembic/

requirements.txt
```

---

# Folder Responsibilities

## api/

Contains

- API Routers
- Versioning
- Route Registration

Never contains business logic.

---

## services/

Contains

Business logic.

Responsible for

- Calculations
- Aggregations
- Analytics
- Data transformations
- Validation

Every feature owns its own service.

Example

```
driver_service.py

race_service.py

constructor_service.py

telemetry_service.py

strategy_service.py
```

---

## repositories/

Responsible only for database interaction.

Repositories never calculate analytics.

Responsibilities

- CRUD
- Query optimization
- Pagination
- Filtering

---

## schemas/

Contains

Pydantic request models.

Pydantic response models.

Validation models.

No database logic.

---

## models/

Contains

SQLAlchemy ORM models.

Represents database tables.

Nothing else.

---

## middleware/

Contains

- Logging
- CORS
- Request timing
- Security headers
- Compression
- Future authentication middleware

---

## database/

Contains

- Engine
- Session
- Base
- Connection configuration

---

## core/

Contains

Global application configuration.

Example

```
settings.py

logging.py

security.py

constants.py
```

---

# Request Lifecycle

```
HTTP Request

↓

Router

↓

Dependency Injection

↓

Service Layer

↓

Repository Layer

↓

Database

↓

Repository

↓

Service

↓

Response Schema

↓

Client
```

Every request follows this path.

No shortcuts.

---

# Service Layer

Services own

- Analytics
- Domain logic
- Computation
- Data aggregation

Services never know

- HTTP
- Frontend
- React

Services should be reusable.

---

# Repository Layer

Repositories own

- SQL
- ORM
- Filtering
- Pagination

Repositories never

- Compute statistics
- Format responses
- Handle HTTP

---

# API Versioning

Structure

```
/api/v1

/api/v2
```

Every route belongs to a version.

Breaking changes require a new version.

---

# Endpoint Categories

Dashboard

```
/dashboard
```

Drivers

```
/drivers

/drivers/{id}
```

Constructors

```
/constructors
```

Races

```
/races
```

Telemetry

```
/telemetry
```

Strategy

```
/strategy
```

Circuits

```
/circuits
```

Season

```
/season
```

Comparison

```
/compare
```

---

# Response Standard

Every response follows

```json
{
  "success": true,
  "data": {},
  "meta": {},
  "timestamp": "",
  "request_id": ""
}
```

Errors follow

```json
{
  "success": false,
  "error": {
      "code": "",
      "message": ""
  },
  "request_id": ""
}
```

Responses remain consistent.

---

# Validation

Every request must be validated.

Never trust client input.

Validation includes

- IDs
- Query parameters
- Pagination
- Filters
- Sorting
- Dates

---

# Error Handling

Errors are centralized.

Categories

400

Bad Request

401

Unauthorized

403

Forbidden

404

Not Found

422

Validation

500

Internal Server Error

Custom exceptions live inside

```
exceptions/
```

---

# Logging

Every request logs

- Timestamp
- Endpoint
- Method
- Duration
- Status Code
- User Agent
- Request ID

Future

JSON structured logging.

---

# Dependency Injection

FastAPI dependencies manage

- Database Session
- Authentication
- Permissions
- Pagination
- Filters

Business logic never creates sessions manually.

---

# Configuration

Environment variables only.

Never hardcode

- API Keys
- Passwords
- Secrets

Configuration managed with

Pydantic Settings.

---

# Database Sessions

One session

Per request.

Automatically closed.

Connection pooling enabled.

---

# Security

Future support

JWT

OAuth2

Rate Limiting

HTTPS

CORS

Input sanitization

Parameterized queries

Secrets management

---

# Performance

Use

Async endpoints

Connection pooling

Indexes

Pagination

Streaming responses

Materialized views

Avoid

N+1 Queries

Blocking calls

Repeated aggregations

---

# Background Tasks

Future tasks

- Data refresh
- Cache warming
- ETL triggers
- Report generation

Should never block requests.

---

# API Documentation

Automatic

Swagger

```
/docs
```

Redoc

```
/redoc
```

Documentation generated automatically.

---

# Health Endpoints

```
/health

/ready

/live
```

Used for deployment monitoring.

---

# Testing Strategy

Unit Tests

Repositories

Services

Utilities

Integration Tests

API Routes

Database

Authentication

Performance Tests

Analytics Queries

Response Time

---

# Future Services

Authentication

Notifications

Live Telemetry

Redis Cache

Prediction Engine

Machine Learning

WebSockets

Streaming

Architecture should support these additions.

---

# Engineering Standards

Never

❌ Execute SQL in routers

❌ Return ORM models

❌ Skip validation

❌ Duplicate business logic

❌ Hardcode configuration

Always

✅ Use dependency injection

✅ Return schemas

✅ Separate repositories

✅ Separate services

✅ Log requests

✅ Handle errors centrally

---

# Engineering Decisions

## Decision 001

FastAPI

Status

✅ Accepted

Reason

Modern async framework with automatic OpenAPI generation and excellent performance.

---

## Decision 002

Repository Pattern

Status

✅ Accepted

Reason

Separates persistence from business logic.

---

## Decision 003

Service Layer

Status

✅ Accepted

Reason

Keeps analytics reusable and independent of transport layers.

---

## Decision 004

SQLAlchemy

Status

✅ Accepted

Reason

Strong typing, mature ecosystem, and excellent PostgreSQL support.

---

## Decision 005

Pydantic

Status

✅ Accepted

Reason

Reliable validation and automatic serialization.

---

## Decision 006

Stateless Backend

Status

✅ Accepted

Reason

Simplifies scaling, deployment, and horizontal expansion.

---

# Definition of Done

The backend is complete when

✓ Every endpoint is typed

✓ Every request is validated

✓ Business logic exists only in services

✓ Database access exists only in repositories

✓ Errors are standardized

✓ Logging is centralized

✓ Documentation is generated automatically

✓ Performance targets are met

✓ Tests pass successfully

✓ New features can be added without architectural refactoring