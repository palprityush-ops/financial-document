import requests

API_BASE_URL = "http://localhost:8000"


def get_all_invoices():
    try:
        response = requests.get(f"{API_BASE_URL}/invoices")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
