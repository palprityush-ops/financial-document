from fastapi import FastAPI, UploadFile, File
import shutil
import os

from db.operations import get_all_invoices, get_high_risk_invoices
from batch_runner import run_batch_pipeline

app = FastAPI(title="Financial Document Analysis API")

UPLOAD_DIR = "batch_texts"

# -------------------------
# Upload Invoice File
# -------------------------
@app.post("/upload-invoice/")
async def upload_invoice(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "status": "uploaded",
        "filename": file.filename
    }

# -------------------------
# Run Batch Pipeline
# -------------------------
@app.post("/run-batch/")
def run_batch():
    summary = run_batch_pipeline()
    return {
        "status": "batch completed",
        "summary": summary
    }

# -------------------------
# Fetch All Invoices
# -------------------------
@app.get("/invoices")
def fetch_all_invoices():
    data = get_all_invoices()
    return {
        "count": len(data),
        "data": data
    }

# -------------------------
# Fetch High Risk Invoices
# -------------------------
@app.get("/invoices/high-risk")
def fetch_high_risk():
    data = get_high_risk_invoices()
    return {
        "count": len(data),
        "data": data
    }
