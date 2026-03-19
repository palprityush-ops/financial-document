# Evidentia — Financial Document Intelligence System

![Python](https://img.shields.io/badge/Python-3.x-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Flask](https://img.shields.io/badge/Flask-Frontend-lightgrey)
![CI](https://github.com/palprityush-ops/financial-document/actions/workflows/ci.yml/badge.svg)
![Tests](https://img.shields.io/badge/Tests-9%20Passing-brightgreen)
![Security](https://img.shields.io/badge/Security-79%2F100-yellow)
![Live](https://img.shields.io/badge/Status-Live-brightgreen)

A production-oriented financial document analysis platform that automates invoice extraction, validation, risk scoring, and explainability through a structured backend processing pipeline and REST API architecture.

---

## 🌐 Live Demo

| Service | URL |
|---|---|
| Frontend | https://evidentia-frontend.onrender.com |
| Backend API | https://financial-document-2.onrender.com |
| API Docs (Swagger) | https://financial-document-2.onrender.com/docs |

---

## 👥 Team

| Name | Roll Number | Role |
|---|---|---|
| Prityush Pal | 2415500358 | Backend, DevOps, CI/CD |
| Ishika Bharti | 2415500206 | Frontend, Testing, Documentation |

**Mentor:** Mr. Preshit Desai
**Institution:** GLA University, Mathura
**Program:** BTech — Computer Science (2024–2026)

---

## Overview

Evidentia transforms unstructured financial documents into structured, validated, and risk-evaluated data for auditability and analytical insight.

The system processes invoices through a multi-stage pipeline that performs:

- OCR text cleaning and preprocessing
- Structured field extraction
- Data validation and integrity checks
- Confidence scoring
- Risk assessment with explainability
- Persistent storage and analytics reporting
- User authentication with JWT tokens
- Rate-limited and secured REST API

The backend is built with FastAPI and exposes secure REST endpoints.
A Flask-based frontend provides an interactive dark-theme dashboard for document exploration and filtering.

---

## Core Capabilities

- Automated invoice field extraction
- Rule-based validation engine
- Risk scoring with explainability output (LOW / MEDIUM / HIGH)
- Confidence scoring mechanism
- Batch processing support with audit logs
- SQLite-based persistence layer
- JWT-based user authentication (Login + Signup)
- API key authentication for protected endpoints
- Rate limiting (5 login attempts/min)
- Security headers (XSS, CSRF, Clickjacking protection)
- Pagination and filtering endpoints
- Continuous Integration with automated testing and formatting checks

---

## System Architecture

```
User (Browser)
  └── Flask Frontend (Dark Theme Dashboard)
        └── FastAPI Backend (REST API)
              └── Processing Pipeline
                    └── SQLite Database
```

### Processing Pipeline Stages

1. OCR Cleaning (`process_text.py`)
2. Field Extraction (`extractor.py`)
3. Validation (`validator.py`)
4. Confidence & Risk Scoring (`analytics/`)
5. Explainability Generation (`analytics/explainability.py`)
6. Persistence (`db/`)
7. CSV Export + Audit Logging

Each processed document is stored with structured metadata and scoring outputs for traceability.

---

## Technology Stack

### Backend
- Python 3.x
- FastAPI
- Uvicorn
- bcrypt (password hashing)
- PyJWT (token authentication)
- slowapi (rate limiting)

### Frontend
- Flask
- HTML / CSS (custom dark theme)
- Bootstrap 5
- Chart.js

### Database
- SQLite (invoices, risk_explanations, users tables)

### DevOps & CI
- GitHub Actions (CI pipeline)
- Render.com (cloud deployment)
- UptimeRobot (uptime monitoring)
- Black (code formatting)
- Pytest (9 automated tests)

---

## Project Structure

```
financial-document/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── analytics/
│   ├── analytics_engine.py
│   ├── batch_metrics.py
│   ├── explainability.py
│   ├── item_analysis.py
│   └── risk_analysis.py
│
├── api/
│   ├── main.py
│   └── schemas.py
│
├── db/
│   ├── database.py
│   ├── operations.py
│   └── finance.db
│
├── frontend/
│   ├── app.py
│   └── templates/
│       ├── layout.html
│       ├── dashboard.html
│       ├── invoices.html
│       ├── upload.html
│       ├── batch.html
│       ├── audit.html
│       ├── login.html
│       └── signup.html
│
├── tests/
│   └── test_basic.py          # 9 automated tests
│
├── batch_runner.py
├── extractor.py
├── validator.py
├── process_text.py
├── export_csv.py
├── requirements.txt
├── .flake8
└── README.md
```

---

## Running the Project Locally

### 1. Clone the Repository

```bash
git clone https://github.com/palprityush-ops/financial-document.git
cd financial-document
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### 3. Start Backend

```bash
uvicorn api.main:app --reload
```

API available at:

```
http://127.0.0.1:8000
```

### 4. Start Frontend

```bash
python frontend/app.py
```

Frontend available at:

```
http://127.0.0.1:5000
```

---

## API Endpoints

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/` | Public | Health check |
| POST | `/auth/signup` | Public | Create new account |
| POST | `/auth/login` | Public | Login and get JWT token |
| POST | `/upload-invoice/` | Protected | Upload invoice file |
| POST | `/run-batch/` | Protected | Run batch pipeline |
| GET | `/invoices` | Public | Fetch all invoices |
| GET | `/invoices/high-risk` | Public | Fetch high risk invoices |
| GET | `/invoices/by-risk` | Public | Filter by risk level |
| GET | `/invoices/by-date` | Public | Filter by date range |
| GET | `/audit` | Protected | Fetch audit logs |

---

## Risk and Explainability Engine

Invoices are evaluated using structured scoring mechanisms based on:

- Missing mandatory fields (bill number, date, totals)
- Inconsistent or mismatched totals
- Suspicious numeric values
- Structural anomalies
- Low extraction confidence score

Each flagged record includes a structured explanation describing why it was categorized as LOW, MEDIUM, or HIGH risk.

---

## Security Features

- JWT token-based authentication (24hr expiry)
- bcrypt password hashing
- Rate limiting on login (5 req/min) and signup (10 req/min)
- Security headers: X-Frame-Options, X-XSS-Protection, X-Content-Type-Options
- API key protection on sensitive endpoints
- Input validation on all auth endpoints

---

## Continuous Integration

The GitHub Actions workflow automatically:

- Installs all dependencies
- Validates code formatting (Black)
- Executes 9 automated tests (Pytest)

The pipeline runs on every push to the main branch.

---

## Testing

Run tests locally:

```bash
pytest tests
```

Check formatting:

```bash
black --check .
```

Current test coverage:

| Test | Status |
|---|---|
| Database initialization | ✅ Pass |
| High risk — missing fields | ✅ Pass |
| Low risk — valid invoice | ✅ Pass |
| Medium risk — partial fields | ✅ Pass |
| Low confidence increases risk | ✅ Pass |
| Batch risk distribution | ✅ Pass |
| Manual review trigger | ✅ Pass |
| No manual review | ✅ Pass |
| Empty batch handling | ✅ Pass |

---

## Authors

**Prityush Pal** — 2415500358
BTech Computer Science — GLA University, Mathura

**Ishika Bharti** — 2415500206
BTech Computer Science — GLA University, Mathura

**Mentor:** Mr. Preshit Desai
