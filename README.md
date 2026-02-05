
---

## 🔍 Core Features

### ✔ Extraction
- Header fields (bill number, invoice date, totals)
- Item-level extraction with quantity, rate, and totals

### ✔ Validation
- Item-level total validation
- Subtotal consistency check
- Subtotal + tax = grand total validation
- All mismatches logged as issues

### ✔ Confidence & Risk Scoring
- Confidence score (0.0 – 1.0) based on:
  - Missing fields
  - Validation failures
- Risk levels: LOW / MEDIUM / HIGH

### ✔ Batch Analytics
- Total invoices processed
- Risk distribution
- High-risk percentage
- Item price variance detection

### ✔ Explainability
Each invoice includes a `risk_explanation` field describing:
- Low confidence
- Validation mismatches
- Missing or suspicious data

### ✔ Audit Trail
A permanent audit log records:
- Invoice source
- Risk level
- Explanation reasons
- Timestamp

### ✔ Reporting & Export
- `batch_output.json` – structured batch output
- `exports/invoices_export.csv` – Excel-compatible export
- `reports/batch_summary.txt` – human-readable summary
- `reports/batch_report.pdf` – professional PDF report

---

## ▶️ How to Run

### Batch Processing (Main Pipeline)
```bash
python batch_runner.py
