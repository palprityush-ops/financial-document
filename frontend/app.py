from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_BASE = "http://localhost:8000"
API_KEY = "secret-admin-key"


def api_headers():
    return {"x-api-key": API_KEY}


@app.route("/")
def dashboard():

    r = requests.get(f"{API_BASE}/invoices")
    data = r.json()

    invoices = data.get("data", [])

    total = len(invoices)
    high = len([i for i in invoices if i["risk"] == "high"])
    medium = len([i for i in invoices if i["risk"] == "medium"])
    low = len([i for i in invoices if i["risk"] == "low"])

    return render_template(
        "dashboard.html", total=total, high=high, medium=medium, low=low
    )


@app.route("/invoices")
def invoices():

    r = requests.get(f"{API_BASE}/invoices")
    data = r.json()

    invoices = data.get("data", [])

    return render_template("invoices.html", invoices=invoices)


@app.route("/batch", methods=["GET", "POST"])
def batch():

    message = None

    if request.method == "POST":

        r = requests.post(f"{API_BASE}/run-batch/", headers=api_headers())

        message = r.json()

    return render_template("batch.html", message=message)


@app.route("/audit")
def audit():

    r = requests.get(f"{API_BASE}/audit", headers=api_headers())

    data = r.json()

    logs = data.get("data", [])

    return render_template("audit.html", logs=logs)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
