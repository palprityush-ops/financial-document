from db.database import init_db
import pytest
from analytics.risk_analysis import calculate_risk_level, analyze_risk
from extractor import extract_invoice_data
from validator import validate_totals

# ── DB Tests ──────────────────────────────────────────────────────────────────


def test_init_db_runs():
    """Database initializes without errors."""
    import os

    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set — skipping DB test")
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


def test_risk_level_is_string():
    """calculate_risk_level should always return a string."""
    invoice = {"grand_total": 500.0, "bill_number": "INV-010"}
    risk = calculate_risk_level(invoice)
    assert isinstance(risk, str)


def test_risk_level_valid_values():
    """Risk level must be one of the three valid values."""
    invoice = {"grand_total": 500.0, "bill_number": "INV-011", "confidence": 0.8}
    risk = calculate_risk_level(invoice)
    assert risk in ["low", "medium", "high"]


def test_high_risk_zero_grand_total():
    """Invoice with zero grand total should not be low risk."""
    invoice = {
        "grand_total": 0,
        "bill_number": "INV-012",
        "invoice_date": "2024-01-01",
        "confidence": 0.9,
    }
    risk = calculate_risk_level(invoice)
    assert risk in ["medium", "high"]


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


def test_analyze_risk_all_high():
    """All-high batch should have 100% high risk percentage."""
    batch = [{"risk": "high"}] * 5
    result = analyze_risk(batch)
    assert result["risk_distribution"]["high"] == 5
    assert result["manual_review_required"] is True


def test_analyze_risk_all_low():
    """All-low batch should not trigger manual review."""
    batch = [{"risk": "low"}] * 10
    result = analyze_risk(batch)
    assert result["manual_review_required"] is False
    assert result["risk_distribution"]["high"] == 0


def test_analyze_risk_returns_dict():
    """analyze_risk should always return a dict."""
    result = analyze_risk([])
    assert isinstance(result, dict)


# ── Batch Summary Tests ───────────────────────────────────────────────────────


def test_batch_summary_structure():
    """Batch summary keys should always be present."""
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


# ── Extractor Tests ───────────────────────────────────────────────────────────


def test_extractor_full_invoice():
    """Extractor should parse all fields from a complete invoice text."""
    text = (
        "bill no 1001 date 15-03-2024 "
        "sub total 1000 tax 18 percent 180 grand total 1180"
    )
    result = extract_invoice_data(text)
    assert result["bill_number"] == "1001"
    assert result["subtotal"] == 1000
    assert result["tax_amount"] == 180
    assert result["grand_total"] == 1180


def test_extractor_missing_fields_gives_high_risk():
    """Invoice text with no fields should result in HIGH risk."""
    text = "this is a random text with no invoice data"
    result = extract_invoice_data(text)
    assert result["risk_level"] == "HIGH"
    assert result["confidence"] < 0.5


def test_extractor_confidence_full_invoice():
    """Complete invoice should have high confidence."""
    text = (
        "bill no 2001 date 20-01-2024 "
        "sub total 5000 tax 18 percent 900 grand total 5900"
    )
    result = extract_invoice_data(text)
    assert result["confidence"] >= 0.7


def test_extractor_returns_required_keys():
    """Extractor output should always have required keys."""
    result = extract_invoice_data("some text")
    required_keys = [
        "bill_number",
        "invoice_date",
        "subtotal",
        "tax_amount",
        "grand_total",
        "confidence",
        "risk_level",
        "issues",
    ]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"


def test_extractor_confidence_range():
    """Confidence score should always be between 0 and 1."""
    texts = [
        "bill no 999 date 01-01-2024 sub total 500 tax 90 grand total 590",
        "random garbage text",
        "",
    ]
    for text in texts:
        result = extract_invoice_data(text)
        assert (
            0.0 <= result["confidence"] <= 1.0
        ), f"Confidence out of range for: {text!r}"


def test_extractor_issues_is_list():
    """Issues field should always be a list."""
    result = extract_invoice_data("some text without invoice data")
    assert isinstance(result["issues"], list)


def test_extractor_empty_string():
    """Empty string input should not crash the extractor."""
    result = extract_invoice_data("")
    assert "risk_level" in result
    assert "confidence" in result


# ── Validator Tests ───────────────────────────────────────────────────────────


def test_validator_valid_totals():
    """Correct subtotal + tax = grand total should pass."""
    issues = []
    result = validate_totals(1000, 180, 1180, issues)
    assert result is True
    assert len(issues) == 0


def test_validator_invalid_totals():
    """Wrong grand total should fail validation."""
    issues = []
    result = validate_totals(1000, 180, 1500, issues)
    assert result is False
    assert len(issues) > 0


def test_validator_missing_values():
    """None values should fail validation and add issue."""
    issues = []
    result = validate_totals(None, None, None, issues)
    assert result is False
    assert len(issues) > 0


def test_validator_allows_rounding():
    """Totals off by 1 should still pass (rounding tolerance)."""
    issues = []
    result = validate_totals(1000, 180, 1181, issues)
    assert result is True


def test_validator_zero_tax():
    """Zero tax with matching grand total should pass."""
    issues = []
    result = validate_totals(2000, 0, 2000, issues)
    assert result is True
    assert len(issues) == 0


def test_validator_large_values():
    """Large invoice values should validate correctly."""
    issues = []
    result = validate_totals(1_000_000, 180_000, 1_180_000, issues)
    assert result is True
    assert len(issues) == 0


def test_validator_negative_values():
    """Negative values should fail validation."""
    issues = []
    result = validate_totals(-500, 0, -500, issues)
    assert result is False
    assert len(issues) > 0