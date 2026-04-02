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
import shutil, os, bcrypt, jwt, datetime, io
from pydantic import BaseModel

from db.operations import (
    get_audit_logs,
    get_invoices_by_risk,
    get_invoices_by_date,
    get_all_invoices,
    get_high_risk_invoices,
    save_user,
    get_user_by_username,
    get_all_users,
    update_user_role,
    count_users,
    delete_invoice,
    update_user_password,
)
from db.database import init_db
from batch_runner import run_batch_pipeline

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Evidentia — Financial Document Intelligence API",
    description="""
## Evidentia API

A production-grade REST API for automated financial document analysis.

### Roles
- **admin** — Full access: upload, batch, audit, user management
- **user** — Read-only: dashboard and invoices

### Team
- Prityush Pal (2415500358)
- Ishika Bharti (2415500206)
- Mentor: Mr. Preshit Desai, GLA University
    """,
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.on_event("startup")
def startup():
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"DB init failed: {e}")


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


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


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


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


@app.get("/", summary="Health Check", tags=["System"])
def health_check():
    return {"status": "ok", "message": "Financial Document Analysis API running"}


@app.post(
    "/auth/signup",
    summary="Create a new user account",
    description="First user to sign up becomes admin. All others get 'user' role.",
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
        raise HTTPException(status_code=400, detail="This username is already taken.")

    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()

    try:
        total = count_users()
        role = "admin" if total == 0 else "user"
    except Exception:
        role = "user"

    try:
        save_user(req.username.strip(), req.email.strip(), hashed, role)
        return {
            "message": f"Account created successfully. Welcome, {req.username}.",
            "role": role,
        }
    except Exception as e:
        error_msg = str(e).lower()
        if "unique" in error_msg or "duplicate" in error_msg:
            raise HTTPException(
                status_code=400, detail="This email address is already registered."
            )
        raise HTTPException(
            status_code=500, detail=f"Account creation failed: {str(e)}"
        )


@app.post("/auth/login", summary="Authenticate user", tags=["Authentication"])
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


@app.post(
    "/auth/change-password",
    summary="Change user password",
    tags=["Authentication"],
)
@limiter.limit("5/minute")
def change_password(request: Request, req: ChangePasswordRequest):
    user = get_user_by_username(req.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not bcrypt.checkpw(req.old_password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")
    if len(req.new_password) < 6:
        raise HTTPException(
            status_code=400, detail="New password must be at least 6 characters."
        )
    if req.old_password == req.new_password:
        raise HTTPException(
            status_code=400,
            detail="New password must be different from current password.",
        )
    new_hashed = bcrypt.hashpw(req.new_password.encode(), bcrypt.gensalt()).decode()
    update_user_password(req.username, new_hashed)
    return {"message": "Password changed successfully."}


@app.post(
    "/upload-invoice/", summary="Upload .txt invoice", tags=["Invoice Processing"]
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


@app.post("/upload-pdf/", summary="Upload PDF invoice", tags=["Invoice Processing"])
async def upload_pdf(file: UploadFile = File(...), _: str = Depends(verify_api_key)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are supported.")
    try:
        import pdfplumber

        contents = await file.read()
        text = ""
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            raise HTTPException(
                status_code=400, detail="No text could be extracted from this PDF."
            )

        txt_filename = file.filename.replace(".pdf", ".txt")
        with open(os.path.join(UPLOAD_DIR, txt_filename), "w", encoding="utf-8") as f:
            f.write(text)

        return {
            "status": "uploaded",
            "filename": txt_filename,
            "original": file.filename,
            "message": f"PDF converted and saved as '{txt_filename}'",
        }
    except ImportError:
        raise HTTPException(
            status_code=500, detail="PDF processing library not available."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")


@app.post("/run-batch/", summary="Run batch pipeline", tags=["Invoice Processing"])
def run_batch(_: str = Depends(verify_api_key)):
    try:
        summary = run_batch_pipeline()
        return {"status": "batch completed", "batch_summary": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Batch processing failed: {str(e)}"
        )


@app.get("/invoices", summary="Fetch all invoices", tags=["Invoices"])
def fetch_all_invoices(
    limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)
):
    data = get_all_invoices(limit=limit, offset=offset)
    return {"limit": limit, "offset": offset, "count": len(data), "data": data}


@app.get("/invoices/high-risk", summary="Fetch high risk invoices", tags=["Invoices"])
def fetch_high_risk(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    data = get_high_risk_invoices(limit=limit, offset=offset)
    return {"limit": limit, "offset": offset, "count": len(data), "data": data}


@app.get("/invoices/by-risk", summary="Filter by risk level", tags=["Invoices"])
def fetch_invoices_by_risk(
    risk: str = Query(...),
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


@app.get("/invoices/by-date", summary="Filter by date range", tags=["Invoices"])
def fetch_invoices_by_date(
    start_date: str = Query(...),
    end_date: str = Query(...),
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


@app.delete(
    "/invoices/{invoice_id}",
    summary="Delete an invoice by ID",
    tags=["Invoices"],
)
def remove_invoice(invoice_id: int, _: str = Depends(verify_api_key)):
    try:
        deleted = delete_invoice(invoice_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Invoice not found.")
        return {"message": f"Invoice {invoice_id} deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.get("/audit", summary="Fetch audit logs", tags=["Audit"])
def fetch_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: str = Depends(verify_api_key),
):
    data = get_audit_logs(limit, offset)
    return {"limit": limit, "offset": offset, "count": len(data), "data": data}


@app.get("/admin/users", summary="List all users", tags=["Admin"])
def list_users(_: str = Depends(verify_api_key)):
    users = get_all_users()
    return {"total": len(users), "users": users}


@app.post("/admin/promote/{username}", summary="Promote user to admin", tags=["Admin"])
def promote_user(username: str, _: str = Depends(verify_api_key)):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    update_user_role(username, "admin")
    return {"message": f"{username} promoted to admin."}


@app.post("/admin/demote/{username}", summary="Demote admin to user", tags=["Admin"])
def demote_user(username: str, _: str = Depends(verify_api_key)):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    update_user_role(username, "user")
    return {"message": f"{username} demoted to user."}
