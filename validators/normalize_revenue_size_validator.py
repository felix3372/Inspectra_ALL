# validators/normalize_revenue_size_validator.py

def normalize_revenue_size_validator(wb, ws):
    """
    Normalizes the 'Revenue Size' column by replacing:
    - 'Million' → 'M'
    - 'Billion' → 'B'
    Example: "50 Million USD" → "50 M USD"
    """
    headers = [str(cell.value).strip().lower() for cell in ws[1]]

    try:
        col_revenue = headers.index("revenue size") + 1
    except ValueError:
        raise Exception("❌ 'Revenue Size' column not found.")

    for row in ws.iter_rows(min_row=2):
        cell = row[col_revenue - 1]
        value = str(cell.value or "").strip()

        if value:
            updated = value.replace("Million", "M").replace("million", "M")
            updated = updated.replace("Billion", "B").replace("billion", "B")
            updated = updated.replace("MILLION", "M").replace("BILLION", "B")
            cell.value = updated

    return wb, ws
