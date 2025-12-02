import re

def normalize_linkedin_company_link(wb, ws):
    headers = [cell.value for cell in ws[1]]

    try:
        col_linkedin = headers.index("Company Linkedin Link") + 1
    except ValueError:
        return wb, ws  # Column not present — skip validator

    for row in range(2, ws.max_row + 1):
        cell = ws.cell(row, col_linkedin)
        original = str(cell.value or "").strip()

        # Skip non-LinkedIn links
        if not original.lower().startswith("http") or "linkedin.com" not in original.lower():
            continue

        # Match company page base
        match = re.match(r"(https?://(www\.)?linkedin\.com/company/[^/?#]+)", original, re.IGNORECASE)
        if match:
            base = match.group(1)
            cell.value = f"{base}/about/"

    return wb, ws
