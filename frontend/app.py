import os
import random
from datetime import datetime, timedelta

import requests
from flask import Flask, abort, redirect, render_template, request, session, url_for

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "evidentia_flask_secret_2024")

API_BASE = os.environ.get("API_BASE", "https://financial-document-2.onrender.com")
API_KEY = os.environ.get("API_KEY", "secret-admin-key")

# Admin secret key — set this in your .env file
ADMIN_SECRET_KEY = os.environ.get("ADMIN_SECRET_KEY", "evidentia_admin_2024")

# In-memory OTP store — use Redis in production
# Format: { email: { otp: "123456", expires: datetime } }
_otp_store = {}


def api_headers():
    return {"x-api-key": API_KEY}


def login_required():
    if "username" not in session:
        return redirect(url_for("login"))
    return None


def admin_required():
    if "username" not in session:
        return redirect(url_for("login"))
    if session.get("role") != "admin":
        abort(403)
    return None


def _generate_otp():
    return "".join(random.choices("0123456789", k=6))


@app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "error.html",
            code=404,
            title="Page Not Found",
            message="The page you are looking for does not exist.",
            username=session.get("username"),
        ),
        404,
    )


@app.errorhandler(500)
def internal_server_error(e):
    return (
        render_template(
            "error.html",
            code=500,
            title="Internal Server Error",
            message="Something went wrong on our end. Please try again later.",
            username=session.get("username"),
        ),
        500,
    )


@app.errorhandler(403)
def forbidden(e):
    return (
        render_template(
            "error.html",
            code=403,
            title="Access Denied",
            message="You do not have permission to access this page. Admin access required.",
            username=session.get("username"),
        ),
        403,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("dashboard"))

    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "user")
        admin_key = request.form.get("admin_key", "").strip()

        if not username or not password:
            error = "Please enter both username and password."

        # ── ADMIN LOGIN ───────────────────────────────────────────────────────
        elif role == "admin":
            if admin_key != ADMIN_SECRET_KEY:
                error = "Invalid admin secret key."
            else:
                try:
                    r = requests.post(
                        f"{API_BASE}/auth/login",
                        json={"username": username, "password": password},
                        timeout=30,
                    )
                    if r.status_code == 200:
                        data = r.json()
                        if data.get("role", "user") != "admin":
                            error = "This account does not have admin privileges."
                        else:
                            session["username"] = data.get("username", username)
                            session["role"] = "admin"
                            session["token"] = data.get("token")
                            return redirect(url_for("dashboard"))
                    else:
                        error = r.json().get(
                            "detail", "Invalid credentials. Please try again."
                        )
                except Exception:
                    error = "Unable to connect to the server. Please try again later."

        # ── USER LOGIN ────────────────────────────────────────────────────────
        else:
            try:
                r = requests.post(
                    f"{API_BASE}/auth/login",
                    json={"username": username, "password": password},
                    timeout=30,
                )
                if r.status_code == 200:
                    data = r.json()
                    session["username"] = data.get("username", username)
                    session["role"] = data.get("role", "user")
                    session["token"] = data.get("token")
                    return redirect(url_for("dashboard"))
                else:
                    error = r.json().get(
                        "detail", "Invalid credentials. Please try again."
                    )
            except Exception:
                error = "Unable to connect to the server. Please try again later."

    return render_template("login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "username" in session:
        return redirect(url_for("dashboard"))
    error = None
    success = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not email or not password:
            error = "All fields are required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        else:
            try:
                r = requests.post(
                    f"{API_BASE}/auth/signup",
                    json={"username": username, "email": email, "password": password},
                    timeout=30,
                )
                if r.status_code == 200:
                    success = "Account created successfully. Please sign in."
                else:
                    error = r.json().get(
                        "detail", "This username or email is already registered."
                    )
            except Exception:
                error = "Unable to connect to the server. Please try again later."
    return render_template("signup.html", error=error, success=success)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if "username" in session:
        return redirect(url_for("dashboard"))

    show_otp = False
    show_newpw = False
    show_success = False
    submitted_email = None
    submitted_otp = None
    error = None

    if request.method == "POST":
        step = request.form.get("step", "email")

        # ── STEP 1: Send OTP ──────────────────────────────────────────────────
        if step == "email":
            email = request.form.get("email", "").strip()
            submitted_email = email

            if not email:
                error = "Please enter your email address."
            else:
                otp = _generate_otp()
                _otp_store[email] = {
                    "otp": otp,
                    "expires": datetime.utcnow() + timedelta(minutes=10),
                }
                try:
                    r = requests.post(
                        f"{API_BASE}/auth/send-otp",
                        json={"email": email, "otp": otp},
                        headers=api_headers(),
                        timeout=10,
                    )
                    if r.status_code != 200:
                        print(f"[DEV] OTP for {email}: {otp}")
                except Exception:
                    print(f"[DEV] OTP for {email}: {otp}")

                show_otp = True

        # ── STEP 2: Verify OTP ────────────────────────────────────────────────
        elif step == "otp":
            email = request.form.get("email", "").strip()
            otp = request.form.get("otp", "").strip()
            submitted_email = email
            submitted_otp = otp

            record = _otp_store.get(email)
            if not record:
                error = "Session expired. Please request a new code."
                submitted_email = None
            elif datetime.utcnow() > record["expires"]:
                _otp_store.pop(email, None)
                error = "Code expired. Please request a new one."
                submitted_email = None
            elif record["otp"] != otp:
                error = "Invalid code. Please try again."
                show_otp = True
            else:
                show_newpw = True

        # ── STEP 3: Reset Password ────────────────────────────────────────────
        elif step == "reset":
            email = request.form.get("email", "").strip()
            otp = request.form.get("otp", "").strip()
            new_password = request.form.get("new_password", "").strip()
            confirm_pw = request.form.get("confirm_password", "").strip()

            if new_password != confirm_pw:
                error = "Passwords do not match."
                show_newpw = True
                submitted_email = email
                submitted_otp = otp
            elif len(new_password) < 6:
                error = "Password must be at least 6 characters."
                show_newpw = True
                submitted_email = email
                submitted_otp = otp
            else:
                try:
                    r = requests.post(
                        f"{API_BASE}/auth/reset-password",
                        json={
                            "email": email,
                            "otp": otp,
                            "new_password": new_password,
                        },
                        headers=api_headers(),
                        timeout=15,
                    )
                    if r.status_code == 200:
                        _otp_store.pop(email, None)
                        show_success = True
                    else:
                        error = r.json().get(
                            "detail", "Password reset failed. Please try again."
                        )
                        show_newpw = True
                        submitted_email = email
                        submitted_otp = otp
                except Exception:
                    error = "Unable to connect to the server. Please try again later."
                    show_newpw = True
                    submitted_email = email
                    submitted_otp = otp

    return render_template(
        "forgot_password.html",
        error=error,
        show_otp=show_otp,
        show_newpw=show_newpw,
        show_success=show_success,
        submitted_email=submitted_email,
        submitted_otp=submitted_otp,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    check = login_required()
    if check:
        return check
    error = None
    success = None
    if request.method == "POST":
        old_password = request.form.get("old_password", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        if not old_password or not new_password or not confirm_password:
            error = "All fields are required."
        elif len(new_password) < 6:
            error = "New password must be at least 6 characters."
        elif new_password != confirm_password:
            error = "New passwords do not match."
        else:
            try:
                r = requests.post(
                    f"{API_BASE}/auth/change-password",
                    json={
                        "username": session["username"],
                        "old_password": old_password,
                        "new_password": new_password,
                    },
                    timeout=15,
                )
                if r.status_code == 200:
                    success = "Password changed successfully."
                else:
                    error = r.json().get("detail", "Password change failed.")
            except Exception:
                error = "Unable to connect to the server. Please try again later."
    return render_template(
        "profile.html",
        error=error,
        success=success,
        username=session.get("username"),
        role=session.get("role"),
    )


@app.route("/")
def dashboard():
    check = login_required()
    if check:
        return check
    try:
        r = requests.get(f"{API_BASE}/invoices", timeout=5)
        data = r.json()
        invoices = data.get("data", [])
    except Exception:
        invoices = []
    total = len(invoices)
    high = len([i for i in invoices if str(i.get("risk", "")).lower() == "high"])
    medium = len([i for i in invoices if str(i.get("risk", "")).lower() == "medium"])
    low = len([i for i in invoices if str(i.get("risk", "")).lower() == "low"])
    return render_template(
        "dashboard.html",
        total=total,
        high=high,
        medium=medium,
        low=low,
        username=session.get("username"),
        role=session.get("role"),
    )


@app.route("/invoices")
def invoices():
    check = login_required()
    if check:
        return check
    try:
        r = requests.get(f"{API_BASE}/invoices?limit=100", timeout=5)
        data = r.json()
        invoices = data.get("data", [])
    except Exception:
        invoices = []
    return render_template(
        "invoices.html",
        invoices=invoices,
        username=session.get("username"),
        role=session.get("role"),
    )


@app.route("/invoices/delete/<int:invoice_id>", methods=["POST"])
def delete_invoice(invoice_id):
    check = admin_required()
    if check:
        return check
    try:
        requests.delete(
            f"{API_BASE}/invoices/{invoice_id}",
            headers=api_headers(),
            timeout=10,
        )
    except Exception:
        pass
    return redirect(url_for("invoices"))


# ── ADMIN ONLY ROUTES ─────────────────────────────────────────────────────────


@app.route("/upload", methods=["GET", "POST"])
def upload():
    check = admin_required()
    if check:
        return check
    message = None
    success = False
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            message = "No file selected. Please choose a .txt or .pdf invoice file."
        else:
            filename = file.filename.lower()
            if filename.endswith(".pdf"):
                try:
                    r = requests.post(
                        f"{API_BASE}/upload-pdf/",
                        files={"file": (file.filename, file.stream, "application/pdf")},
                        headers=api_headers(),
                        timeout=30,
                    )
                    if r.status_code == 200:
                        data = r.json()
                        message = (
                            f"PDF '{file.filename}' uploaded and converted successfully! "
                            f"Saved as '{data.get('filename')}'. Ready for batch processing."
                        )
                        success = True
                    else:
                        message = (
                            f"Upload failed: {r.json().get('detail', 'Unknown error')}"
                        )
                except Exception as e:
                    message = f"Could not connect to API: {str(e)}"
            elif filename.endswith(".txt"):
                try:
                    r = requests.post(
                        f"{API_BASE}/upload-invoice/",
                        files={"file": (file.filename, file.stream, "text/plain")},
                        headers=api_headers(),
                        timeout=30,
                    )
                    if r.status_code == 200:
                        message = f"'{file.filename}' uploaded successfully! Ready for batch processing."
                        success = True
                    else:
                        message = (
                            f"Upload failed: {r.json().get('detail', 'Unknown error')}"
                        )
                except Exception as e:
                    message = f"Could not connect to API: {str(e)}"
            else:
                message = "Invalid file type. Only .txt and .pdf files are supported."
    return render_template(
        "upload.html",
        message=message,
        success=success,
        username=session.get("username"),
        role=session.get("role"),
    )


@app.route("/batch", methods=["GET", "POST"])
def batch():
    check = admin_required()
    if check:
        return check
    message = None
    if request.method == "POST":
        try:
            r = requests.post(
                f"{API_BASE}/run-batch/", headers=api_headers(), timeout=30
            )
            message = r.json()
        except Exception as e:
            message = {"status": "error", "detail": str(e)}
    return render_template(
        "batch.html",
        message=message,
        username=session.get("username"),
        role=session.get("role"),
    )


@app.route("/audit")
def audit():
    check = admin_required()
    if check:
        return check
    try:
        r = requests.get(f"{API_BASE}/audit", headers=api_headers(), timeout=5)
        data = r.json()
        logs = data.get("data", [])
    except Exception:
        logs = []
    return render_template(
        "audit.html",
        logs=logs,
        username=session.get("username"),
        role=session.get("role"),
    )


@app.route("/admin/users")
def admin_users():
    check = admin_required()
    if check:
        return check
    try:
        r = requests.get(f"{API_BASE}/admin/users", headers=api_headers(), timeout=10)
        users = r.json().get("users", [])
    except Exception:
        users = []
    return render_template(
        "admin_users.html",
        users=users,
        username=session.get("username"),
        role=session.get("role"),
    )


@app.route("/admin/promote/<username>", methods=["POST"])
def promote_user(username):
    check = admin_required()
    if check:
        return check
    try:
        requests.post(
            f"{API_BASE}/admin/promote/{username}", headers=api_headers(), timeout=10
        )
    except Exception:
        pass
    return redirect(url_for("admin_users"))


@app.route("/admin/demote/<username>", methods=["POST"])
def demote_user(username):
    check = admin_required()
    if check:
        return check
    if username == session.get("username"):
        return redirect(url_for("admin_users"))
    try:
        requests.post(
            f"{API_BASE}/admin/demote/{username}", headers=api_headers(), timeout=10
        )
    except Exception:
        pass
    return redirect(url_for("admin_users"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
