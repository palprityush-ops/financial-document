from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_BASE = "http://localhost:8000"
API_KEY = "secret-admin-key"


def api_headers():
    return {"x-api-key": API_KEY}


# ── Dashboard ────────────────────────────────────────────────────────────────
@app.route("/")
def dashboard():
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
    )


# ── Invoices ─────────────────────────────────────────────────────────────────
@app.route("/invoices")
def invoices():
    try:
        r = requests.get(f"{API_BASE}/invoices?limit=100", timeout=5)
        data = r.json()
        invoices = data.get("data", [])
    except Exception:
        invoices = []

    return render_template("invoices.html", invoices=invoices)


# ── Upload ───────────────────────────────────────────────────────────────────
@app.route("/upload", methods=["GET", "POST"])
def upload():
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
                    timeout=10,
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

    return render_template("upload.html", message=message, success=success)


# ── Batch ────────────────────────────────────────────────────────────────────
@app.route("/batch", methods=["GET", "POST"])
def batch():
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

    return render_template("batch.html", message=message)


# ── Audit ────────────────────────────────────────────────────────────────────
@app.route("/audit")
def audit():
    try:
        r = requests.get(f"{API_BASE}/audit", headers=api_headers(), timeout=5)
        data = r.json()
        logs = data.get("data", [])
    except Exception:
        logs = []

    return render_template("audit.html", logs=logs)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
