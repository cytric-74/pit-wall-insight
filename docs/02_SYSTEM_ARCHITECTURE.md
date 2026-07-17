# SYSTEM ARCHITECTURE

# Pit Wall Insight

Version: 1.0

Status: Planning

---

# Overview

Pit Wall Insight follows a modular, production-inspired architecture that separates responsibilities into independent services while maintaining a cohesive development experience.

The platform is designed around four primary layers:

- Data Layer
- Backend Layer
- Frontend Layer
- Infrastructure Layer

Each layer is independently maintainable, scalable, and deployable.

The architecture prioritizes:

- Maintainability
- Scalability
- Performance
- Developer Experience
- Type Safety
- Separation of Concerns

---

# High-Level Architecture

```text
                        Formula One APIs
                               │
                               ▼
                   Python Data Ingestion Service
                               │
                               ▼
                     PostgreSQL (Raw Database)
                               │
                               ▼
                     dbt Transformation Layer
                               │
                               ▼
                 PostgreSQL (Analytics Database)
                               │
                               ▼
                         FastAPI Backend
                               │
                 REST API / Future GraphQL
                               │
                               ▼
                  React + TypeScript Frontend
                               │
                               ▼
                          End User
```

---

# Repository Structure

```text
pit-wall-insight/

├── apps/
│   ├── frontend/
│   ├── backend/
│   └── ingestion/
│
├── warehouse/
│   ├── dbt/
│   ├── sql/
│   └── seeds/
│
├── packages/
│   ├── shared-types/
│   ├── ui/
│   ├── config/
│   └── utils/
│
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   └── scripts/
│
├── docs/
│
├── .github/
│
└── README.md
```

---

# Architecture Principles

Every architectural decision follows these principles:

- Single Responsibility
- Feature Isolation
- Shared Types
- Modular Services
- API First
- Independent Deployability
- Clear Boundaries
- High Cohesion
- Low Coupling

---

# Layer Overview

## Data Layer

Responsible for collecting, validating, cleaning and transforming Formula One data.

Responsibilities

- API ingestion
- Data validation
- Cleaning
- Historical storage
- ETL pipelines
- dbt transformations

Technology

- Python
- FastF1
- Ergast API
- PostgreSQL
- dbt

---

## Backend Layer

Acts as the central communication layer between frontend and database.

Responsibilities

- Business logic
- Authentication (future)
- Aggregations
- Analytics queries
- API responses
- Caching
- Validation

Technology

- FastAPI
- SQLAlchemy
- Pydantic
- Alembic

---

## Frontend Layer

Responsible for presentation and user experience.

Responsibilities

- UI
- Charts
- Filtering
- Routing
- State management
- Animations
- User interactions

Technology

- React
- TypeScript
- TailwindCSS
- Framer Motion
- TanStack Query
- Zustand
- D3 / Apache ECharts

---

## Infrastructure Layer

Responsible for deployment and automation.

Responsibilities

- Docker
- CI/CD
- Hosting
- Environment management
- Monitoring
- Reverse proxy

Technology

- Docker
- Docker Compose
- GitHub Actions
- Vercel
- Railway / Render
- Nginx

---

# Data Flow

## Ingestion Pipeline

```text
FastF1 API

↓

Python Collectors

↓

Validation

↓

Cleaning

↓

Raw PostgreSQL Tables

↓

dbt Models

↓

Analytics Tables
```

---

## Backend Flow

```text
Client Request

↓

API Router

↓

Service Layer

↓

Repository Layer

↓

Analytics Database

↓

Pydantic Response

↓

Frontend
```

---

## Frontend Flow

```text
React Component

↓

TanStack Query

↓

FastAPI Endpoint

↓

Cache

↓

Render UI
```

---

# Monorepo Strategy

Pit Wall Insight uses a monorepo architecture.

Reasons

- Shared types
- Shared utilities
- Shared UI components
- Easier dependency management
- Single CI/CD pipeline
- Consistent tooling

---

# Package Responsibilities

## apps/frontend

Owns

- Pages
- Components
- Layout
- Charts
- Animations
- Theme

Never

- Query database directly
- Perform business logic

---

## apps/backend

Owns

- API
- Services
- Authentication
- Validation
- Business Logic

Never

- Render UI
- Store frontend state

---

## apps/ingestion

Owns

- Data collection
- Scheduling
- ETL
- Validation

Never

- Serve APIs
- Render frontend

---

## warehouse

Owns

- SQL models
- dbt
- Fact tables
- Dimension tables
- Analytics marts

---

## packages/ui

Owns

Reusable components

Example

- Button
- Modal
- Drawer
- Card
- Tabs
- Charts
- Tooltips

---

## packages/shared-types

Owns

Shared interfaces

Example

```typescript
Driver

Constructor

Race

Lap

Telemetry

PitStop
```

Used by

- Backend
- Frontend
- Data Pipeline

---

# API Architecture

```
Client

↓

Routes

↓

Controllers

↓

Services

↓

Repositories

↓

Database
```

Every layer has one responsibility.

---

# Database Strategy

Two logical databases.

Raw Layer

Stores untouched data.

Analytics Layer

Stores optimized analytical tables.

Benefits

- Reproducibility
- Easier debugging
- Better performance
- Cleaner transformations

---

# Caching Strategy

Client

TanStack Query

↓

API Cache

↓

Database

Future

Redis

---

# Error Handling

Errors should be categorized.

Validation Errors

Authentication Errors

API Errors

Database Errors

Unexpected Errors

Every error should include

- status code
- message
- request id
- timestamp

---

# Logging Strategy

Every service logs

- requests
- execution time
- failures
- warnings
- pipeline execution

Future

Structured JSON logging.

---

# Security Principles

Never expose

- database credentials
- API keys
- secrets
- environment variables

Environment variables stored separately.

Input validation required for every endpoint.

Parameterized SQL only.

---

# Scalability Strategy

Future support includes

- Redis
- GraphQL
- WebSockets
- Live telemetry
- Multiple workers
- Load balancing
- Horizontal scaling

Architecture should require minimal changes.

---

# Performance Strategy

Backend

- Async endpoints
- Connection pooling
- Query optimization

Frontend

- Lazy loading
- Code splitting
- Virtualization
- Memoization

Database

- Proper indexing
- Materialized views
- Analytics tables

---

# Deployment Architecture

```text
GitHub

↓

GitHub Actions

↓

Build

↓

Test

↓

Docker Images

↓

Deploy

↓

Vercel

↓

Railway / Render

↓

Production
```

---

# Environment Separation

Development

Local Docker

↓

Testing

CI Environment

↓

Production

Cloud Infrastructure

Every environment should remain isolated.

---

# Architecture Constraints

The system must

✓ Remain modular

✓ Support additional seasons

✓ Support new APIs

✓ Support cloud deployment

✓ Support machine learning modules

✓ Support real-time telemetry

✓ Support mobile clients in the future

Without requiring architectural redesign.

---

# Engineering Decisions

## Decision 001

Architecture Style

Modular Monorepo

Status

✅ Accepted

Reason

Simplifies dependency management and promotes code reuse.

---

## Decision 002

Backend Framework

FastAPI

Status

✅ Accepted

Reason

High performance, automatic OpenAPI documentation, async support, excellent Python ecosystem.

---

## Decision 003

Frontend Framework

React + TypeScript

Status

✅ Accepted

Reason

Industry standard, scalable component architecture, strong ecosystem.

---

## Decision 004

Database

PostgreSQL

Status

✅ Accepted

Reason

Excellent analytical capabilities, reliability, extensibility, compatibility with dbt.

---

## Decision 005

Transformation Layer

dbt

Status

✅ Accepted

Reason

Encourages modular SQL, testing, documentation, and analytics engineering best practices.

---

## Decision 006

Repository Pattern

Service + Repository Architecture

Status

✅ Accepted

Reason

Separates business logic from persistence layer and improves maintainability.

---

## Definition of Done

The architecture is considered complete when

✓ Layers are clearly separated

✓ Dependencies are unidirectional

✓ Every service has a single responsibility

✓ Shared code is reusable

✓ Infrastructure is containerized

✓ CI/CD is operational

✓ Documentation is synchronized with implementation

✓ Architecture supports future expansion without major refactoring