import os

from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)

# Session ke liye secret key zaroori hai
app.secret_key = os.environ.get("SECRET_KEY", "evidentia_flask_secret_2024")

API_BASE = os.environ.get("API_BASE", "https://financial-document-2.onrender.com")
API_KEY = os.environ.get("API_KEY", "secret-admin-key")


def api_headers():
    return {"x-api-key": API_KEY}


# ── Login Required Helper ─────────────────────────────────────────────────────
def login_required():
    """Agar logged in nahi hai toh login pe redirect karo"""
    if "username" not in session:
        return redirect(url_for("login"))
    return None


# ── Login ─────────────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    # Agar pehle se logged in hai toh dashboard pe bhejo
    if "username" in session:
        return redirect(url_for("dashboard"))

    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            error = "Please enter both username and password."
        else:
            try:
                r = requests.post(
                    f"{API_BASE}/auth/login",
                    json={"username": username, "password": password},
                    timeout=30,
                )
                if r.status_code == 200:
                    data = r.json()
                    session["username"] = data["username"]
                    session["role"] = data["role"]
                    session["token"] = data["token"]
                    return redirect(url_for("dashboard"))
                else:
                    error = r.json().get("detail", "Invalid credentials. Please try again.")
            except Exception as e:
                error = "Unable to connect to the server. Please try again later."

    return render_template("login.html", error=error)


# ── Signup ────────────────────────────────────────────────────────────────────
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Agar pehle se logged in hai toh dashboard pe bhejo
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
                    error = r.json().get("detail", "This username or email is already registered.")
            except Exception as e:
                error = "Unable to connect to the server. Please try again later."

    return render_template("signup.html", error=error, success=success)


# ── Logout ────────────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── Dashboard ─────────────────────────────────────────────────────────────────
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
    )


# ── Invoices ──────────────────────────────────────────────────────────────────
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
    )


# ── Upload ────────────────────────────────────────────────────────────────────
@app.route("/upload", methods=["GET", "POST"])
def upload():
    check = login_required()
    if check:
        return check

    message = None
    success = False

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            message = "No file selected. Please choose a .txt invoice file."
        elif not file.filename.endswith(".txt"):
            message = "Invalid file type. Only .txt files are supported."
        else:
            try:
                r = requests.post(
                    f"{API_BASE}/upload-invoice/",
                    files={"file": (file.filename, file.stream, "text/plain")},
                    headers=api_headers(),
                    timeout=30,
                )
                if r.status_code == 200:
                    message = (
                        f"'{file.filename}' uploaded successfully!"
                        " Ready for batch processing."
                    )
                    success = True
                else:
                    message = (
                        f"Upload failed: {r.json().get('detail', 'Unknown error')}"
                    )
            except Exception as e:
                message = f"Could not connect to API: {str(e)}"

    return render_template(
        "upload.html",
        message=message,
        success=success,
        username=session.get("username"),
    )


# ── Batch ─────────────────────────────────────────────────────────────────────
@app.route("/batch", methods=["GET", "POST"])
def batch():
    check = login_required()
    if check:
        return check

    message = None

    if request.method == "POST":
        try:
            r = requests.post(
                f"{API_BASE}/run-batch/",
                headers=api_headers(),
                timeout=30,
            )
            message = r.json()
        except Exception as e:
            message = {"status": "error", "detail": str(e)}

    return render_template(
        "batch.html",
        message=message,
        username=session.get("username"),
    )


# ── Audit ─────────────────────────────────────────────────────────────────────
@app.route("/audit")
def audit():
    check = login_required()
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
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
