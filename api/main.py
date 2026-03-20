from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Query,
    Header,
    Depends,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
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
from db.database import init_db
from batch_runner import run_batch_pipeline

# -------------------------
# Rate Limiter Setup
# -------------------------
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Evidentia — Financial Document Intelligence API",
    description="""
## Evidentia API

A production-grade REST API for automated financial document analysis.

### Features
- **Invoice Processing** — Extract, validate and score financial documents
- **Risk Assessment** — LOW / MEDIUM / HIGH risk classification with explainability
- **Batch Processing** — Process multiple invoices in one pipeline run
- **User Authentication** — JWT-based secure login and signup
- **Audit Logging** — Full processing trail for every document

### Authentication
Protected endpoints require an API key in the `x-api-key` header.

### Team
- Prityush Pal (2415500358)
- Ishika Bharti (2415500206)
- Mentor: Mr. Preshit Desai, GLA University
    """,
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# -------------------------
# Startup — DB init
# -------------------------
@app.on_event("startup")
def startup():
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"DB init failed: {e}")


# -------------------------
# Security Headers Middleware
# -------------------------
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "batch_texts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

API_KEY = "secret-admin-key"
SECRET_KEY = "evidentia_jwt_secret_2024"


# -------------------------
# Pydantic Models
# -------------------------
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


# -------------------------
# Security: API Key
# -------------------------
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


# -------------------------
# Security: JWT Token
# -------------------------
def verify_token(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, detail="Session expired. Please sign in again."
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")


# -------------------------
# Health Check
# -------------------------
@app.get(
    "/",
    summary="Health Check",
    description="Returns API status. Use this to verify the service is running.",
    tags=["System"],
)
def health_check():
    return {"status": "ok", "message": "Financial Document Analysis API running"}


# -------------------------
# SIGNUP
# -------------------------
@app.post(
    "/auth/signup",
    summary="Create a new user account",
    description="Register a new user with username, email and password. Password must be at least 6 characters. Rate limited to 10 requests per minute.",
    tags=["Authentication"],
)
@limiter.limit("10/minute")
def signup(request: Request, req: SignupRequest):
    if len(req.username.strip()) < 3:
        raise HTTPException(
            status_code=400, detail="Username must be at least 3 characters."
        )
    if len(req.password) < 6:
        raise HTTPException(
            status_code=400, detail="Password must be at least 6 characters long."
        )

    existing = get_user_by_username(req.username.strip())
    if existing:
        raise HTTPException(
            status_code=400,
            detail="This username is already taken. Please choose another.",
        )

    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()

    try:
        save_user(req.username.strip(), req.email.strip(), hashed)
        return {"message": f"Account created successfully. Welcome, {req.username}."}
    except Exception as e:
        error_msg = str(e).lower()
        if "unique" in error_msg or "duplicate" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="This email address is already registered.",
            )
        raise HTTPException(
            status_code=500,
            detail=f"Account creation failed: {str(e)}",
        )


# -------------------------
# LOGIN
# -------------------------
@app.post(
    "/auth/login",
    summary="Authenticate user and get JWT token",
    description="Login with username and password. Returns a JWT token valid for 24 hours. Rate limited to 5 requests per minute.",
    tags=["Authentication"],
)
@limiter.limit("5/minute")
def login(request: Request, req: LoginRequest):
    user = get_user_by_username(req.username)

    if not user:
        raise HTTPException(
            status_code=401, detail="No account found with this username."
        )

    if not bcrypt.checkpw(req.password.encode(), user["password"].encode()):
        raise HTTPException(
            status_code=401, detail="Incorrect password. Please try again."
        )

    token = jwt.encode(
        {
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        },
        SECRET_KEY,
        algorithm="HS256",
    )

    return {
        "token": token,
        "username": user["username"],
        "role": user["role"],
        "message": "Login successful.",
    }


# -------------------------
# Upload Invoice
# -------------------------
@app.post(
    "/upload-invoice/",
    summary="Upload an invoice file for processing",
    description="Upload a .txt invoice file to the batch processing queue. Requires API key authentication. Only .txt format is supported.",
    tags=["Invoice Processing"],
)
async def upload_invoice(
    file: UploadFile = File(...), _: str = Depends(verify_api_key)
):
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=400, detail="Only .txt invoice files are supported"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    return {"status": "uploaded", "filename": file.filename}


# -------------------------
# Run Batch Pipeline
# -------------------------
@app.post(
    "/run-batch/",
    summary="Run the batch processing pipeline",
    description="Processes all uploaded invoice files through the full pipeline: extraction, validation, risk scoring, explainability and persistence. Requires API key.",
    tags=["Invoice Processing"],
)
def run_batch(_: str = Depends(verify_api_key)):
    try:
        summary = run_batch_pipeline()
        return {"status": "batch completed", "batch_summary": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Batch processing failed: {str(e)}"
        )


# -------------------------
# Fetch All Invoices
# -------------------------
@app.get(
    "/invoices",
    summary="Fetch all processed invoices",
    description="Returns a paginated list of all processed invoices. Supports limit and offset for pagination.",
    tags=["Invoices"],
)
def fetch_all_invoices(
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
):
    data = get_all_invoices(limit=limit, offset=offset)
    return {"limit": limit, "offset": offset, "count": len(data), "data": data}


# -------------------------
# Fetch High Risk Invoices
# -------------------------
@app.get(
    "/invoices/high-risk",
    summary="Fetch high risk invoices only",
    description="Returns only invoices classified as HIGH risk. Useful for prioritizing manual review.",
    tags=["Invoices"],
)
def fetch_high_risk(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    data = get_high_risk_invoices(limit=limit, offset=offset)
    return {"limit": limit, "offset": offset, "count": len(data), "data": data}


# -------------------------
# Fetch by Risk
# -------------------------
@app.get(
    "/invoices/by-risk",
    summary="Filter invoices by risk level",
    description="Filter invoices by risk level. Accepted values: low, medium, high.",
    tags=["Invoices"],
)
def fetch_invoices_by_risk(
    risk: str = Query(..., description="Risk level: low, medium, or high"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    risk = risk.lower()
    if risk not in ["low", "medium", "high"]:
        raise HTTPException(status_code=400, detail="Risk must be: low, medium, high")
    data = get_invoices_by_risk(risk, limit, offset)
    return {
        "risk": risk,
        "limit": limit,
        "offset": offset,
        "count": len(data),
        "data": data,
    }


# -------------------------
# Fetch by Date
# -------------------------
@app.get(
    "/invoices/by-date",
    summary="Filter invoices by date range",
    description="Returns invoices processed within a given date range. Date format: YYYY-MM-DD.",
    tags=["Invoices"],
)
def fetch_invoices_by_date(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    data = get_invoices_by_date(start_date, end_date, limit, offset)
    return {
        "start_date": start_date,
        "end_date": end_date,
        "count": len(data),
        "data": data,
    }


# -------------------------
# Audit Logs
# -------------------------
@app.get(
    "/audit",
    summary="Fetch audit logs",
    description="Returns a full audit trail of all processed invoices including risk reasons. Requires API key authentication.",
    tags=["Audit"],
)
def fetch_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: str = Depends(verify_api_key),
):
    data = get_audit_logs(limit, offset)
    return {"limit": limit, "offset": offset, "count": len(data), "data": data}
