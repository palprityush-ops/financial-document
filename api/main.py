from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, bcrypt, jwt, datetime
from pydantic import BaseModel

from db.operations import (
    get_audit_logs,
    get_invoices_by_risk,
    get_invoices_by_date,
    get_all_invoices,
    get_high_risk_invoices,
    save_user,
    get_user_by_username,
)
from db.database import init_db  # ✅ ADDED
from batch_runner import run_batch_pipeline

app = FastAPI(title="Financial Document Analysis API")

# ✅ ADDED — startup pe teeno tables ban jaayengi
@app.on_event("startup")
def startup():
    init_db()

# CORS — frontend se call allow karne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "batch_texts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ⚠️ Inhe baad mein .env mein daalna
API_KEY    = "secret-admin-key"
SECRET_KEY = "evidentia_jwt_secret_2024"

# -------------------------
# Pydantic Models (Request body ke liye)
# -------------------------
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

# -------------------------
# Security: API Key (purana system — rakho as is)
# -------------------------
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# -------------------------
# Security: JWT Token verify (nayi login ke liye)
# -------------------------
def verify_token(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload  # {"user_id", "username", "role"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expire ho gaya, dobara login karo")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalid hai")

# -------------------------
# Health Check (PUBLIC)
# -------------------------
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Financial Document Analysis API running"}

# -------------------------
# SIGNUP
# -------------------------
@app.post("/auth/signup")
def signup(req: SignupRequest):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password kam se kam 6 characters ka hona chahiye")
    
    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    
    try:
        save_user(req.username, req.email, hashed)
        return {"message": f"Account ban gaya! Welcome, {req.username}"}
    except Exception:
        raise HTTPException(status_code=400, detail="Username ya email already registered hai")

# -------------------------
# LOGIN
# -------------------------
@app.post("/auth/login")
def login(req: LoginRequest):
    user = get_user_by_username(req.username)
    
    if not user:
        raise HTTPException(status_code=401, detail="Username nahi mila")
    
    if not bcrypt.checkpw(req.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Password galat hai")
    
    token = jwt.encode({
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")
    
    return {
        "token": token,
        "username": user["username"],
        "role": user["role"],
        "message": "Login successful!"
    }

# -------------------------
# Upload Invoice (PROTECTED — purana API key system rakha)
# -------------------------
@app.post("/upload-invoice/")
async def upload_invoice(
    file: UploadFile = File(...), _: str = Depends(verify_api_key)
):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt invoice files are supported")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    return {"status": "uploaded", "filename": file.filename}

# -------------------------
# Run Batch Pipeline (PROTECTED)
# -------------------------
@app.post("/run-batch/")
def run_batch(_: str = Depends(verify_api_key)):
    try:
        summary = run_batch_pipeline()
        return {"status": "batch completed", "batch_summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

# -------------------------
# Fetch All Invoices (PUBLIC)
# -------------------------
@app.get("/invoices")
def fetch_all_invoices(
    limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)
):
    data = get_all_invoices(limit=limit, offset=offset)
    return {"limit": limit, "offset": offset, "count": len(data), "data": data}

# -------------------------
# Fetch High Risk Invoices (PUBLIC)
# -------------------------
@app.get("/invoices/high-risk")
def fetch_high_risk(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    data = get_high_risk_invoices(limit=limit, offset=offset)
    return {"limit": limit, "offset": offset, "count": len(data), "data": data}

# -------------------------
# Fetch by Risk (PUBLIC)
# -------------------------
@app.get("/invoices/by-risk")
def fetch_invoices_by_risk(
    risk: str, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)
):
    risk = risk.lower()
    if risk not in ["low", "medium", "high"]:
        raise HTTPException(status_code=400, detail="Risk must be: low, medium, high")
    data = get_invoices_by_risk(risk, limit, offset)
    return {"risk": risk, "limit": limit, "offset": offset, "count": len(data), "data": data}

# -------------------------
# Fetch by Date (PUBLIC)
# -------------------------
@app.get("/invoices/by-date")
def fetch_invoices_by_date(
    start_date: str, end_date: str,
    limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
):
    data = get_invoices_by_date(start_date, end_date, limit, offset)
    return {"start_date": start_date, "end_date": end_date, "count": len(data), "data": data}

# -------------------------
# Audit Logs (PROTECTED)
# -------------------------
@app.get("/audit")
def fetch_audit_logs(
    limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
    _: str = Depends(verify_api_key),
):
    data = get_audit_logs(limit, offset)
    return {"limit": limit, "offset": offset, "count": len(data), "data": data}
