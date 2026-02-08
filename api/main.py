from fastapi import FastAPI, UploadFile, File, HTTPException, Query
import shutil
import os

from db.operations import get_audit_logs
from db.operations import get_invoices_by_risk
from db.operations import get_invoices_by_date
from db.operations import get_all_invoices, get_high_risk_invoices
from batch_runner import run_batch_pipeline

# -------------------------
# App init
# -------------------------
app = FastAPI(title="Financial Document Analysis API")

UPLOAD_DIR = "batch_texts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------
# Health Check
# -------------------------
@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Financial Document Analysis API running"
    }

# -------------------------
# Upload Invoice File
# -------------------------
@app.post("/upload-invoice/")
async def upload_invoice(file: UploadFile = File(...)):
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
# Run Batch Pipeline
# -------------------------
@app.post("/run-batch/")
def run_batch():
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
# Fetch All Invoices (PAGINATED)
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
# Fetch High Risk Invoices (PAGINATED)
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

@app.get("/audit")
def fetch_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    data = get_audit_logs(limit, offset)
    return {
        "limit": limit,
        "offset": offset,
        "count": len(data),
        "data": data
    }
