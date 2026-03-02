from extractor import extract_fields


def test_extract_fields_returns_dict():
    result = extract_fields("Sample invoice text")
    assert isinstance(result, dict)
