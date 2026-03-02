Evidentia — Financial Document Intelligence System

Evidentia is a production-oriented financial document analysis platform that automates invoice extraction, validation, risk scoring, and explainability through a structured backend processing pipeline and REST API architecture.

The system transforms unstructured financial documents into structured, validated, and risk-evaluated data for auditability and analytical insight.

Overview

Evidentia processes financial documents through a multi-stage pipeline that performs:

OCR text cleaning and preprocessing

Structured field extraction

Data validation and integrity checks

Confidence scoring

Risk assessment

Explainability generation

Persistent storage and analytics reporting

The backend is built with FastAPI and exposes secure REST endpoints.
A Streamlit-based frontend provides an interactive dashboard for exploration and filtering.

Key Capabilities

Automated invoice field extraction

Rule-based validation engine

Risk scoring with explainability output

Confidence scoring mechanism

Batch processing support

SQLite-based persistence layer

API key–based authentication

Pagination and filtering endpoints

Continuous Integration with automated testing and formatting checks

System Architecture

Client (Streamlit UI or API consumer)
→ FastAPI Application Layer
→ Processing Pipeline
→ SQLite Database

Processing Pipeline Stages

OCR Cleaning (process_text.py)

Field Extraction (extractor.py)

Validation (validator.py)

Confidence & Risk Scoring (analytics/)

Explainability Generation

Persistence (db/)

Each processed document is stored with structured metadata and scoring outputs for traceability.

Technology Stack
Backend

Python 3.x

FastAPI

Uvicorn

Frontend

Streamlit

Database

SQLite

Analytics Layer

Custom rule-based risk and explainability engine

Code Quality & CI

Black (formatting)

Pytest (testing)

GitHub Actions (CI pipeline)

Project Structure
financial-document/
│
├── .github/workflows/
│   └── ci.yml                    # GitHub Actions CI pipeline
│
├── analytics/                    # Risk, metrics & explainability engine
│   ├── analytics_engine.py
│   ├── batch_metrics.py
│   ├── explainability.py
│   ├── item_analysis.py
│   └── risk_analysis.py
│
├── api/                          # FastAPI backend
│   ├── main.py                   # API entry point
│   └── schemas.py                # Pydantic models
│
├── db/                           # Database layer
│   ├── database.py               # SQLite connection setup
│   ├── operations.py             # CRUD operations
│   └── finance.db                # SQLite database file
│
├── frontend/                     # Streamlit dashboard
│   ├── app.py                    # Frontend entry point
│   ├── config.py
│   ├── api/                      # API client utilities
│   ├── components/               # Reusable UI components
│   ├── pages/                    # Multi-page views
│   └── utils/
│
├── invoices/
│   └── sample_invoices.pdf
│
├── tests/
│   └── test_basic.py             # Pytest test suite
│
├── batch_runner.py               # Batch execution controller
├── extractor.py                  # Invoice extraction logic
├── validator.py                  # Validation rules engine
├── process_text.py               # OCR text cleaning
├── export_csv.py                 # CSV export utilities
├── export_items_csv.py
│
├── requirements.txt
├── .flake8
├── .gitattributes
├── .gitignore
└── README.md
Running the Project Locally
1. Clone the Repository
git clone https://github.com/YOUR_USERNAME/financial-document.git
cd financial-document
2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
3. Start Backend
uvicorn api.main:app --reload

The API will be available at:

http://127.0.0.1:8000
4. Start Frontend
streamlit run frontend/app.py
API Capabilities

Upload and process invoice documents

Batch processing of multiple invoices

Pagination of processed records

Risk-based filtering

Date-based filtering

Audit endpoint access

API key authentication middleware

Risk and Explainability Engine

The system evaluates invoices using rule-based scoring mechanisms based on:

Missing mandatory fields

Inconsistent dates

Suspicious numeric values

Structural anomalies

Low extraction confidence

Each flagged record includes a structured explanation describing why it was categorized as risky.

Continuous Integration

The project includes a GitHub Actions workflow that automatically:

Installs dependencies

Validates code formatting (Black)

Executes automated tests (Pytest)

The pipeline runs on every push to the main branch to ensure code quality and reproducibility.

Testing

Run tests locally:

pytest tests

Formatting validation:

black --check .
Future Improvements

Integration with production-grade OCR engines

Machine learning–based anomaly detection

Migration to PostgreSQL for production use

Docker containerization

Cloud deployment

Role-based access control

Author

PRITYUSH PAL
ISHIKA BHARTI
BTech — Computer Science
Financial Document Analysis System Project