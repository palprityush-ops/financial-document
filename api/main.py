from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Header, Depends
import shutil
import os

from db.operations import (
    get_audit_logs,
    get_invoices_by_risk,
    get_invoices_by_date,
    get_all_invoices,
    get_high_risk_invoices
)
from batch_runner import run_batch_pipeline

# -------------------------
# App init
# -------------------------
app = FastAPI(title="Financial Document Analysis API")

UPLOAD_DIR = "batch_texts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

API_KEY = "secret-admin-key"

# -------------------------
# Security dependency
# -------------------------
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# -------------------------
# Health Check (PUBLIC)
# -------------------------
@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Financial Document Analysis API running"
    }

# -------------------------
# Upload Invoice File (PROTECTED)
# -------------------------
@app.post("/upload-invoice/")
async def upload_invoice(
    file: UploadFile = File(...),
    _: str = Depends(verify_api_key)
):
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Only .txt invoice files are supported"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )

    return {
        "status": "uploaded",
        "filename": file.filename
    }

# -------------------------
# Run Batch Pipeline (PROTECTED)
# -------------------------
@app.post("/run-batch/")
def run_batch(_: str = Depends(verify_api_key)):
    try:
        summary = run_batch_pipeline()
        return {
            "status": "batch completed",
            "batch_summary": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch processing failed: {str(e)}"
        )

# -------------------------
# Fetch All Invoices (PUBLIC)
# -------------------------
@app.get("/invoices")
def fetch_all_invoices(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    data = get_all_invoices(limit=limit, offset=offset)
    return {
        "limit": limit,
        "offset": offset,
        "count": len(data),
        "data": data
    }

# -------------------------
# Fetch High Risk Invoices (PUBLIC)
# -------------------------
@app.get("/invoices/high-risk")
def fetch_high_risk(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    data = get_high_risk_invoices(limit=limit, offset=offset)
    return {
        "limit": limit,
        "offset": offset,
        "count": len(data),
        "data": data
    }

# -------------------------
# Fetch Invoices by Risk (PUBLIC)
# -------------------------
@app.get("/invoices/by-risk")
def fetch_invoices_by_risk(
    risk: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    risk = risk.lower()
    if risk not in ["low", "medium", "high"]:
        raise HTTPException(
            status_code=400,
            detail="Risk must be one of: low, medium, high"
        )

    data = get_invoices_by_risk(risk, limit, offset)
    return {
        "risk": risk,
        "limit": limit,
        "offset": offset,
        "count": len(data),
        "data": data
    }

# -------------------------
# Fetch Invoices by Date (PUBLIC)
# -------------------------
@app.get("/invoices/by-date")
def fetch_invoices_by_date(
    start_date: str,
    end_date: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    data = get_invoices_by_date(start_date, end_date, limit, offset)
    return {
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit,
        "offset": offset,
        "count": len(data),
        "data": data
    }

# -------------------------
# Audit Logs (PROTECTED)
# -------------------------
@app.get("/audit")
def fetch_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: str = Depends(verify_api_key)
):
    data = get_audit_logs(limit, offset)
    return {
        "limit": limit,
        "offset": offset,
        "count": len(data),
        "data": data
    }
