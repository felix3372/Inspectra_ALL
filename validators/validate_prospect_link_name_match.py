import re

def clean_name_for_link(text):
    """Lowercase and strip special characters for fuzzy link matching."""
    return re.sub(r"[^a-z0-9]", "", text.lower())

def validate_prospect_link_name_match(wb, ws):
    headers = [cell.value for cell in ws[1]]

    try:
        col_first = headers.index("First Name") + 1
        col_last = headers.index("Last Name") + 1
        col_link = headers.index("Linkedin Link Prospect") + 1
    except ValueError:
        return wb, ws  # Required headers not found — skip

    # Add "Prospect Link review" column if missing
    if "Prospect Link review" in headers:
        col_review = headers.index("Prospect Link review") + 1
    else:
        col_review = len(headers) + 1
        ws.cell(row=1, column=col_review).value = "Prospect Link review"

    for row in range(2, ws.max_row + 1):
        first = str(ws.cell(row, col_first).value or "").strip()
        last = str(ws.cell(row, col_last).value or "").strip()
        link = str(ws.cell(row, col_link).value or "").strip().lower()

        if not link or "linkedin.com" not in link:
            continue  # Skip empty or non-LinkedIn links

        f_clean = clean_name_for_link(first)
        l_clean = clean_name_for_link(last)
        link_clean = clean_name_for_link(link)

        if f_clean in link_clean and l_clean in link_clean:
            continue  # ✅ Full match
        elif f_clean in link_clean:
            ws.cell(row, col_review).value = "Only first name found in link"
        elif l_clean in link_clean:
            ws.cell(row, col_review).value = "Only last name found in link"
        else:
            ws.cell(row, col_review).value = "Prospect name not found in link"

    return wb, ws
