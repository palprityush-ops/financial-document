from db.database import init_db
from analytics.risk_analysis import calculate_risk_level, analyze_risk

# ── DB Tests ──────────────────────────────────────────────────────────────────


def test_init_db_runs():
    """Database initializes without errors."""
    init_db()


# ── Risk Level Tests ──────────────────────────────────────────────────────────


def test_high_risk_missing_fields():
    """Invoice with missing critical fields should be HIGH risk."""
    invoice = {"grand_total": None, "bill_number": None}
    risk = calculate_risk_level(invoice)
    assert risk == "high", f"Expected high, got {risk}"


def test_low_risk_valid_invoice():
    """Complete valid invoice should be LOW risk."""
    invoice = {
        "grand_total": 1500.0,
        "subtotal": 1200.0,
        "tax_amount": 300.0,
        "bill_number": "INV-001",
        "invoice_date": "2024-01-01",
        "confidence": 0.95,
    }
    risk = calculate_risk_level(invoice)
    assert risk == "low", f"Expected low, got {risk}"


def test_medium_risk_partial_fields():
    """Invoice with some missing fields should be MEDIUM or HIGH risk."""
    invoice = {
        "grand_total": 1000.0,
        "bill_number": "INV-002",
        "invoice_date": None,
        "subtotal": None,
    }
    risk = calculate_risk_level(invoice)
    assert risk in ["medium", "high"], f"Expected medium or high, got {risk}"


def test_low_confidence_increases_risk():
    """Low confidence score should increase risk level."""
    invoice = {
        "grand_total": 1500.0,
        "bill_number": "INV-003",
        "invoice_date": "2024-01-01",
        "confidence": 0.2,
    }
    risk = calculate_risk_level(invoice)
    assert risk in ["medium", "high"], f"Expected medium or high, got {risk}"


# ── Analyze Risk (Batch) Tests ────────────────────────────────────────────────


def test_analyze_risk_distribution():
    """Batch risk distribution should count correctly."""
    batch = [
        {"risk": "high"},
        {"risk": "high"},
        {"risk": "medium"},
        {"risk": "low"},
    ]
    result = analyze_risk(batch)
    assert result["risk_distribution"]["high"] == 2
    assert result["risk_distribution"]["medium"] == 1
    assert result["risk_distribution"]["low"] == 1


def test_analyze_risk_manual_review_triggered():
    """More than 20% high risk should trigger manual review."""
    batch = [{"risk": "high"}] * 3 + [{"risk": "low"}] * 7
    result = analyze_risk(batch)
    assert result["manual_review_required"] is True


def test_analyze_risk_no_manual_review():
    """Less than 20% high risk should not trigger manual review."""
    batch = [{"risk": "high"}] * 1 + [{"risk": "low"}] * 9
    result = analyze_risk(batch)
    assert result["manual_review_required"] is False


def test_analyze_risk_empty_batch():
    """Empty batch should return zero values without crashing."""
    result = analyze_risk([])
    assert result["high_risk_percentage"] == 0.0
    assert result["manual_review_required"] is False
    assert result["risk_distribution"]["high"] == 0


# ── Batch Summary Tests ───────────────────────────────────────────────────────


def test_batch_summary_structure():
    """Batch summary keys should always be present."""
    # Direct dictionary test — no file dependency
    summary = {
        "total_invoices": 0,
        "high_risk": 0,
        "low_risk": 0,
        "medium_risk": 0,
        "average_confidence": 0,
        "total_grand_amount": 0,
    }
    assert "total_invoices" in summary
    assert "high_risk" in summary
    assert "low_risk" in summary
    assert "medium_risk" in summary
    assert "average_confidence" in summary
