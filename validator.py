def validate_totals(subtotal, tax_amount, grand_total, issues):
    total_valid = False

    if subtotal is None or tax_amount is None or grand_total is None:
        issues.append("Missing values for validation")
        return total_valid

    calculated_total = subtotal + tax_amount

    if abs(calculated_total - grand_total) <= 1:
        total_valid = True
    else:
        issues.append("Subtotal + tax does not match grand total")

    return total_valid
