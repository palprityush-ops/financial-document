import requests

API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30


# -----------------------------
# Internal Request Handler
# -----------------------------

def _request(method, endpoint, **kwargs):
    url = f"{API_BASE_URL}{endpoint}"

    try:
        response = requests.request(
            method=method,
            url=url,
            timeout=TIMEOUT,
            **kwargs
        )
        response.raise_for_status()

        # If response has JSON, return it
        if response.content:
            return response.json()

        return {"status": "success"}

    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error: {str(http_err)}"}

    except requests.exceptions.ConnectionError:
        return {"error": "Connection error. Is backend running?"}

    except requests.exceptions.Timeout:
        return {"error": "Request timed out."}

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# Public API Methods
# -----------------------------

def get_all_invoices():
    return _request("GET", "/invoices")


def get_invoice_by_id(invoice_id):
    return _request("GET", f"/invoices/{invoice_id}")


def upload_invoice(file):
    return _request(
        "POST",
        "/invoices",
        files={"file": file}
    )


def run_batch():
    return _request("POST", "/batch")