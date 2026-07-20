# DEPLOYMENT & DEVOPS

# Pit Wall Insight

Version: 1.0

Status: Planning

---

# Overview

Pit Wall Insight should be deployable using modern DevOps practices.

The deployment architecture prioritizes:

- Simplicity
- Scalability
- Reproducibility
- Observability
- Automation

Every environment should behave consistently.

Development, staging, and production should require minimal configuration changes.

---

# Deployment Philosophy

Deployment should be:

- Automated
- Repeatable
- Containerized
- Versioned
- Observable

No manual deployment steps should be required.

Every deployment should originate from GitHub.

---

# Infrastructure Overview

```text
                    GitHub Repository
                            │
                            ▼
                    GitHub Actions CI/CD
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
       Build Frontend              Build Backend
              │                           │
              ▼                           ▼
          Vercel                     Docker Image
              │                           │
              └─────────────┬─────────────┘
                            ▼
                      Railway / Render
                            │
                            ▼
                      PostgreSQL
                            │
                            ▼
                    End Users
```

---

# Infrastructure Stack

Frontend

- Vercel

Backend

- Railway
- Render

Database

- PostgreSQL

Containerization

- Docker

CI/CD

- GitHub Actions

Monitoring

- UptimeRobot
- Better Stack (Future)

Logging

- Structured Logs

---

# Environment Strategy

Three environments.

```
Development

↓

Staging

↓

Production
```

Each environment has its own

- Database
- Environment Variables
- Deployment
- API URL

---

# Development

Runs locally.

Services

```
Frontend

Backend

PostgreSQL

dbt

Adminer
```

Started using

```bash
docker compose up
```

No cloud dependencies.

---

# Staging

Purpose

Pre-production testing.

Connected to

- Staging Database
- Test API Keys

Automatic deployment

From

```
develop
```

branch.

---

# Production

Purpose

Public deployment.

Automatic deployment

From

```
main
```

after successful CI.

---

# Docker

Every service is containerized.

Containers

```
frontend

backend

postgres

dbt

adminer
```

Future

```
redis

nginx

celery

airflow
```

---

# Docker Compose

Single command

```bash
docker compose up
```

Should start

- React
- FastAPI
- PostgreSQL
- dbt
- Adminer

Entire project operational within minutes.

---

# Git Branch Strategy

```
main

↓

develop

↓

feature/*
```

Examples

```
feature/driver-dashboard

feature/race-replay

feature/telemetry

feature/theme-engine
```

Never commit directly to

```
main
```

---

# GitHub Actions

Pipeline

```
Push

↓

Install Dependencies

↓

Lint

↓

Run Tests

↓

Build Frontend

↓

Build Backend

↓

Run dbt Tests

↓

Build Docker Images

↓

Deploy
```

Every step must succeed.

---

# CI Pipeline

Frontend

- ESLint
- TypeScript
- Unit Tests
- Build

Backend

- Ruff
- Black
- Pytest

Warehouse

- dbt build
- dbt test

Deployment only occurs after successful validation.

---

# Secrets Management

Secrets stored only in

GitHub Secrets

Platform Environment Variables

Never commit

```
.env
```

Never expose

- Database Passwords
- API Keys
- Tokens
- Secrets

---

# Environment Variables

Frontend

```
VITE_API_URL

VITE_APP_NAME

VITE_ENVIRONMENT
```

Backend

```
DATABASE_URL

SECRET_KEY

API_VERSION

LOG_LEVEL

ENVIRONMENT
```

Data Pipeline

```
FASTF1_CACHE

DBT_TARGET

PIPELINE_VERSION
```

---

# Database Deployment

Production PostgreSQL

Automatic Backups

Point-in-time recovery (Future)

SSL Enabled

Indexes created during migration.

---

# Database Migrations

Managed with

Alembic

Migration process

```
Generate

↓

Review

↓

Commit

↓

Deploy

↓

Run Migration
```

Never manually modify production schema.

---

# Deployment Process

Developer

↓

Push Code

↓

GitHub Actions

↓

Tests

↓

Build

↓

Deploy

↓

Health Check

↓

Production

Rollback available if deployment fails.

---

# Health Checks

Backend

```
/health

/ready

/live
```

Frontend

Automatic availability checks.

Deployment succeeds only after healthy responses.

---

# Monitoring

Monitor

- API Availability
- Database Connectivity
- Deployment Status
- Error Rates
- Response Times

Future

Grafana Dashboard

Prometheus

OpenTelemetry

---

# Logging

Every deployment logs

- Version
- Commit Hash
- Deployment Time
- Environment
- Status

Every API logs

- Request ID
- Endpoint
- Execution Time
- Response Status

---

# Performance Targets

Frontend

First Load

<2 seconds

Backend

Average Response

<200ms

Database

Average Query

<100ms

Pipeline

Race Refresh

<3 minutes

---

# CDN

Frontend assets

Served through CDN.

Images optimized.

Fonts preloaded.

Icons tree-shaken.

---

# Security

HTTPS

Enabled

CORS

Configured

Rate Limiting

Not implemented in-process (no middleware/dependency on any route). Required
at the reverse-proxy/API gateway layer (e.g. nginx `limit_req`, an API
gateway, or a CDN's rate-limiting product) before any public deployment —
`/search` and `/strategy/tyres` in particular are unauthenticated and
expensive (Phase 7 audit, High).

JWT

Future

Security Headers

Enabled

SQL Injection

Prevented

Environment Variables

Encrypted

---

# Rollback Strategy

If deployment fails

```
Restore Previous Deployment

↓

Run Health Check

↓

Notify Developer

↓

Open Incident
```

Rollback should require one action.

---

# Backup Strategy

Database

Daily Backup

Weekly Snapshot

Monthly Archive

Retention

30 Days

Future

Disaster Recovery Region

---

# Scaling Strategy

Frontend

Horizontal

Backend

Stateless

Horizontal

Database

Read Replicas (Future)

Redis Cache (Future)

Object Storage (Future)

Architecture should support growth without redesign.

---

# Future Infrastructure

- Kubernetes
- Redis
- Airflow
- Kafka
- Snowflake
- Cloudflare
- Sentry
- Grafana
- Prometheus
- OpenTelemetry

---

# Engineering Decisions

## Decision 001

Docker Everywhere

Status

✅ Accepted

Reason

Ensures consistent environments across development and production.

---

## Decision 002

GitHub Actions

Status

✅ Accepted

Reason

Simple, reliable, and tightly integrated with the repository.

---

## Decision 003

Vercel + Railway

Status

✅ Accepted

Reason

Fast deployments with minimal operational overhead.

---

## Decision 004

Infrastructure as Code Philosophy

Status

✅ Accepted

Reason

Infrastructure should be reproducible, version-controlled, and documented.

---

## Decision 005

Automated Deployments

Status

✅ Accepted

Reason

Reduces manual errors and ensures every deployment passes quality gates.

---

# Definition of Done

The deployment architecture is complete when

✓ Every service is containerized

✓ Local development requires a single startup command

✓ CI/CD pipelines execute automatically

✓ Tests run before deployment

✓ Health checks validate successful deployments

✓ Rollback strategy is documented

✓ Secrets are securely managed

✓ Production deployments are automated

✓ Infrastructure is reproducible

✓ The platform can be deployed by any developer with minimal setup