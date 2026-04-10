<div align="center">

# Evidentia
### Financial Document Intelligence System

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-Frontend-lightgrey?style=flat-square)
![CI](https://github.com/palprityush-ops/financial-document/actions/workflows/ci.yml/badge.svg)
![Tests](https://img.shields.io/badge/Tests-9%20Passing-brightgreen?style=flat-square)
![Security](https://img.shields.io/badge/Security-79%2F100-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=flat-square)

**Automates invoice extraction, validation, risk scoring, and explainability through a structured backend pipeline and REST API.**

[Live Demo](https://evidentia-frontend.onrender.com) · [API Docs](https://financial-document-2.onrender.com/docs) · [Backend API](https://financial-document-2.onrender.com)

</div>

---

## Overview

Evidentia transforms unstructured financial documents into structured, validated, and risk-evaluated data for auditability and analytical insight.

The system processes invoices through a multi-stage pipeline:

```
OCR Cleaning → Field Extraction → Validation → Risk Scoring → Explainability → Storage
```

The backend is built with **FastAPI** and exposes secure REST endpoints. A **Flask** frontend provides an interactive dark-theme dashboard with visual risk scoring, per-invoice explainability panels, and portfolio-level analytics.

---

## Features

| Feature | Description |
|---|---|
| 📄 Invoice Extraction | Automated field extraction from uploaded documents |
| ✅ Validation Engine | Rule-based integrity checks on extracted data |
| 🎯 Risk Scoring | LOW / MEDIUM / HIGH classification with confidence scores |
| 🔍 Explainability | Per-invoice breakdown of risk factors with visual indicators |
| 📊 Dashboard Analytics | Portfolio risk exposure meter, charts, and trend views |
| 🔐 Authentication | JWT-based login/signup with bcrypt password hashing |
| 🛡️ Security | CSRF protection, rate limiting, security headers |
| 📦 Batch Processing | Bulk invoice pipeline with audit logs |
| 🔄 CI/CD | GitHub Actions with automated tests and formatting checks |

---

## Live Services

| Service | URL |
|---|---|
| Frontend | https://evidentia-frontend.onrender.com |
| Backend API | https://financial-document-2.onrender.com |
| Swagger Docs | https://financial-document-2.onrender.com/docs |

---

## Tech Stack

**Backend** — Python 3.x, FastAPI, Uvicorn, PyJWT, bcrypt, slowapi

**Frontend** — Flask, HTML/CSS (dark theme), Bootstrap 5, Chart.js, Flask-WTF

**Database** — SQLite (`invoices`, `risk_explanations`, `users` tables)

**DevOps** — GitHub Actions, Render.com, Docker (GHCR), UptimeRobot, Black, Pytest

---

## System Architecture

```
Browser
  └── Flask Frontend  (dark theme dashboard, risk visualization)
        └── FastAPI Backend  (REST API, JWT auth, rate limiting)
              └── Processing Pipeline
                    ├── OCR Cleaning         process_text.py
                    ├── Field Extraction     extractor.py
                    ├── Validation           validator.py
                    ├── Risk & Confidence    analytics/
                    ├── Explainability       analytics/explainability.py
                    └── Persistence          db/
```

---

## Project Structure

```
financial-document/
├── .github/workflows/
│   ├── ci.yml
│   └── publish-images.yml
├── analytics/
│   ├── analytics_engine.py
│   ├── batch_metrics.py
│   ├── explainability.py
│   ├── item_analysis.py
│   └── risk_analysis.py
├── api/
│   ├── main.py
│   └── schemas.py
├── db/
│   ├── database.py
│   ├── operations.py
│   └── finance.db
├── frontend/
│   ├── app.py
│   └── templates/
│       ├── layout.html
│       ├── dashboard.html
│       ├── invoices.html        ← risk visualization + explainability
│       ├── upload.html
│       ├── batch.html
│       ├── audit.html
│       ├── login.html
│       └── signup.html
├── tests/
│   └── test_basic.py
├── batch_runner.py
├── extractor.py
├── validator.py
├── process_text.py
├── export_csv.py
├── Dockerfile.backend
├── Dockerfile.frontend
├── render.yaml
└── requirements.txt
```

---

## Local Setup

### 1. Clone

```bash
git clone https://github.com/palprityush-ops/financial-document.git
cd financial-document
```

### 2. Virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

### 3. Start backend

```bash
uvicorn api.main:app --reload
# → http://127.0.0.1:8000
```

### 4. Start frontend

```bash
python frontend/app.py
# → http://127.0.0.1:5000
```

---

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Public | Health check |
| POST | `/auth/signup` | Public | Create account |
| POST | `/auth/login` | Public | Login → JWT token |
| POST | `/upload-invoice/` | JWT | Upload invoice file |
| POST | `/run-batch/` | JWT | Run batch pipeline |
| GET | `/invoices` | Public | All invoices |
| GET | `/invoices/high-risk` | Public | High-risk invoices |
| GET | `/invoices/by-risk` | Public | Filter by risk level |
| GET | `/invoices/by-date` | Public | Filter by date range |
| GET | `/audit` | JWT | Audit logs |

Full interactive docs at `/docs` (Swagger UI).

---

## Risk & Explainability Engine

Each invoice is evaluated against:

- Missing mandatory fields (bill number, date, totals)
- Total mismatch (subtotal + tax ≠ grand total)
- Suspicious or anomalous numeric values
- Structural extraction anomalies
- Low confidence score from OCR stage

Every flagged invoice includes a structured explanation panel in the frontend showing which checks failed and why the risk level was assigned.

---

## Security

- JWT authentication (24-hour expiry)
- bcrypt password hashing
- CSRF protection on all POST forms (Flask-WTF)
- Rate limiting — login: 5 req/min, signup: 10 req/min
- Security headers: `X-Frame-Options`, `X-XSS-Protection`, `X-Content-Type-Options`
- API key protection on sensitive endpoints

---

## Tests

```bash
pytest tests           # run all tests
black --check .        # check formatting
```

| Test | Status |
|---|---|
| Database initialization | ✅ |
| High risk — missing fields | ✅ |
| Low risk — valid invoice | ✅ |
| Medium risk — partial fields | ✅ |
| Low confidence increases risk | ✅ |
| Batch risk distribution | ✅ |
| Manual review trigger | ✅ |
| No manual review | ✅ |
| Empty batch handling | ✅ |

---

## Deployment on Render

If Render fails with clone errors (`Could not resolve host: github.com`), deploy from prebuilt Docker images instead.

1. Push to `main` — GitHub Actions will publish images to GHCR automatically.
2. In Render, create two web services using **existing image** deploy mode:
   - `ghcr.io/palprityush-ops/financial-document-backend:latest`
   - `ghcr.io/palprityush-ops/financial-document-frontend:latest`
3. Health check path for both: `/healthz`
4. Set environment variables:
   - Frontend: `API_BASE`, `API_KEY`, `SECRET_KEY`, `ADMIN_SECRET_KEY`
   - Backend: `API_KEY`, JWT secret values

Images do not auto-deploy on push — trigger manually or configure deploy hooks via `RENDER_DEPLOY_HOOK_BACKEND` / `RENDER_DEPLOY_HOOK_FRONTEND`.

---

## Team

| Name | Roll Number | Role |
|---|---|---|
| Prityush Pal | 2415500358 | Backend, DevOps, CI/CD |
| Ishika Bharti | 2415500206 | Frontend, Testing, Documentation |

**Mentor:** Mr. Preshit Desai  
**Institution:** GLA University, Mathura — BTech Computer Science (2024–2026)