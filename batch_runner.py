import os
import json
from datetime import datetime

from utils import clean_text
from extractor import extract_invoice_data
from validator import validate_totals

from db.operations import insert_invoice
from db.database import init_db
from analytics.analytics_engine import run_batch_analytics
from reports.report_generator import generate_text_report
from analytics.explainability import explain_invoice_risk
from export_csv import export_invoices_to_csv
from reports.pdf_report_generator import generate_pdf_report


INPUT_DIR = "batch_texts"
OUTPUT_FILE = "batch_output.json"


def run_batch_pipeline():
    init_db()
    results = []

    # -------------------------
    # Process each invoice file
    # -------------------------
    for file in os.listdir(INPUT_DIR):
        if not file.endswith(".txt"):
            continue

        file_path = os.path.join(INPUT_DIR, file)

        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned_text = clean_text(raw_text)
        extracted = extract_invoice_data(cleaned_text)

        total_valid = validate_totals(
            extracted["subtotal"],
            extracted["tax_amount"],
            extracted["grand_total"],
            extracted["issues"]
        )

        extracted["validation"] = {
            "total_match": total_valid,
            "issues": extracted["issues"]
        }

        extracted["source_file"] = file

        # Normalize fields for analytics
        extracted["total_amount"] = extracted.get("grand_total", 0)
        extracted["risk"] = extracted.get("risk_level", "LOW").lower()

        results.append(extracted)

    # -------------------------
    # Batch summary calculation
    # -------------------------
    total_invoices = len(results)

    low_risk = 0
    medium_risk = 0
    high_risk = 0

    total_confidence = 0
    total_grand_amount = 0

    for r in results:
        total_confidence += r.get("confidence", 0)
        total_grand_amount += r.get("grand_total", 0)

        if r.get("risk_level") == "LOW":
            low_risk += 1
        elif r.get("risk_level") == "MEDIUM":
            medium_risk += 1
        elif r.get("risk_level") == "HIGH":
            high_risk += 1

    batch_summary = {
        "total_invoices": total_invoices,
        "low_risk": low_risk,
        "medium_risk": medium_risk,
        "high_risk": high_risk,
        "average_confidence": round(
            total_confidence / total_invoices, 2
        ) if total_invoices > 0 else 0,
        "total_grand_amount": total_grand_amount
    }

    # -------------------------
    # Final JSON output
    # -------------------------
    final_output = {
        "invoices": results,
        "batch_summary": batch_summary
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)

    print("Batch processing complete. Output saved to", OUTPUT_FILE)

    # -------------------------
    # Analytics + Report
    # -------------------------
    analytics_result = run_batch_analytics(results)
    generate_text_report(analytics_result)
    print("Batch analytics report generated.")

    # -------------------------
    # Explainability
    # -------------------------
    for inv in results:
        inv["risk_explanation"] = explain_invoice_risk(inv)

    print("Risk explainability added.")

    for inv in results:
     insert_invoice(inv)

    print("Invoices persisted to database.")


    # -------------------------
    # CSV Export
    # -------------------------
    export_invoices_to_csv()
    print("Invoice CSV export generated.")

    # -------------------------
    # Audit Log
    # -------------------------
    with open("reports/audit_log.txt", "w", encoding="utf-8") as f:
        f.write("AUDIT LOG - FINANCIAL DOCUMENT ANALYSIS SYSTEM\n")
        f.write("=" * 50 + "\n\n")

        for inv in results:
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Source file: {inv.get('source_file')}\n")
            f.write(f"Risk level: {inv.get('risk')}\n")
            f.write("Reasons:\n")

            for reason in inv.get("risk_explanation", []):
                f.write(f" - {reason}\n")

            f.write("-" * 40 + "\n")

    print("Audit log generated.")

    # -------------------------
    # PDF Report
    # -------------------------
    generate_pdf_report(analytics_result)
    print("PDF report generated.")

    return batch_summary


# -------------------------
# Script entry point
# -------------------------
if __name__ == "__main__":
    run_batch_pipeline()
