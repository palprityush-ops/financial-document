import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z0-9\.\:\-/ ]', '', text)
    return text.strip()

def safe_value(value, label, issues):
    if value is None:
        issues.append(f"{label} not found")
        return None
    return value
