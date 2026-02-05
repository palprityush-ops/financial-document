from analytics.batch_metrics import calculate_batch_metrics
from analytics.risk_analysis import analyze_risk
from analytics.item_analysis import analyze_items


def run_batch_analytics(batch_data):
    batch_metrics = calculate_batch_metrics(batch_data)
    risk_analysis = analyze_risk(batch_data)
    item_analysis = analyze_items(batch_data)

    return {
        "batch_metrics": batch_metrics,
        "risk_analysis": risk_analysis,
        "item_analysis": item_analysis
    }
