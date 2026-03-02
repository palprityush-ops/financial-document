# Evidentia — Financial Document Intelligence System

Evidentia is a production-oriented financial document analysis platform that automates invoice extraction, validation, risk scoring, and explainability through a structured backend processing pipeline and REST API architecture.

The system transforms unstructured financial documents into structured, validated, and risk-evaluated data for auditability and analytical insight.

---

## Overview

Evidentia processes financial documents through a multi-stage pipeline that performs:

- OCR text cleaning and preprocessing  
- Structured field extraction  
- Data validation and integrity checks  
- Confidence scoring  
- Risk assessment  
- Explainability generation  
- Persistent storage and analytics reporting  

The backend is built with FastAPI and exposes secure REST endpoints.  
A Streamlit-based frontend provides an interactive dashboard for exploration and filtering.

---

## Key Capabilities

- Automated invoice field extraction  
- Rule-based validation engine  
- Risk scoring with explainability output  
- Confidence scoring mechanism  
- Batch processing support  
- SQLite-based persistence layer  
- API key–based authentication  
- Pagination and filtering endpoints  
- Continuous Integration with automated testing and formatting checks  

---

## System Architecture

Client (Streamlit UI or API consumer)  
→ FastAPI Application Layer  
→ Processing Pipeline  
→ SQLite Database  

### Processing Pipeline Stages

1. OCR Cleaning (`process_text.py`)  
2. Field Extraction (`extractor.py`)  
3. Validation (`validator.py`)  
4. Confidence & Risk Scoring (`analytics/`)  
5. Explainability Generation  
6. Persistence (`db/`)  

Each processed document is stored with structured metadata and scoring outputs for traceability.

---

## Technology Stack

### Backend
- Python 3.x  
- FastAPI  
- Uvicorn  

### Frontend
- Streamlit  

### Database
- SQLite  

### Analytics Layer
- Custom rule-based risk and explainability engine  

### Code Quality & CI
- Black (formatting)  
- Pytest (testing)  
- GitHub Actions (CI pipeline)  

---

## Project Structure
financial-document/
│
├── .github/workflows/
│ └── ci.yml
│
├── analytics/
│ ├── analytics_engine.py
│ ├── batch_metrics.py
│ ├── explainability.py
│ ├── item_analysis.py
│ └── risk_analysis.py
│
├── api/
│ ├── main.py
│ └── schemas.py
│
├── db/
│ ├── database.py
│ ├── operations.py
│ └── finance.db
│
├── frontend/
│ ├── app.py
│ ├── config.py
│ ├── api/
│ ├── components/
│ ├── pages/
│ └── utils/
│
├── invoices/
│ └── sample_invoices.pdf
│
├── tests/
│ └── test_basic.py
│
├── batch_runner.py
├── extractor.py
├── validator.py
├── process_text.py
├── export_csv.py
├── export_items_csv.py
│
├── requirements.txt
├── .flake8
├── .gitattributes
├── .gitignore
└── README.md

---

## Running the Project Locally

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/financial-document.git
cd financial-document

2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

3. Start Backend
uvicorn api.main:app --reload

API available at:

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

Check formatting:

black --check .
Future Improvements

Integration with production-grade OCR engines

Machine learning–based anomaly detection

Migration to PostgreSQL for production use

Docker containerization

Cloud deployment

Role-based access control

Author

Prityush Pal
BTech — Computer Science
Financial Document Analysis System Project


---

After pasting:

1. Save file  
2. Commit  
3. Push  
4. Refresh GitHub  

Font will now render correctly with proper section separation.

If it still looks wrong, then you pasted outside code fences or removed `#` accidentally.