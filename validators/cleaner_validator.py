import re

def clean_all_data(ws):
    # Only process columns that actually have headers
    header_row = [cell.value for cell in ws[1]]
    used_columns = range(1, len(header_row) + 1)
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=len(header_row)):
        for cell in row:
            if isinstance(cell.value, str):
                cell.value = cell.value.replace('\xa0', ' ').strip()

def format_specific_columns(ws, col_first, col_last, col_email, col_domain, col_phone):
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        # First Name
        cell = row[col_first - 1]
        if isinstance(cell.value, str):
            cell.value = cell.value.title()
        # Last Name
        cell = row[col_last - 1]
        if isinstance(cell.value, str):
            cell.value = cell.value.title()
        # Email & Domain
        cell = row[col_email - 1]
        if isinstance(cell.value, str):
            email_clean = cell.value.lower()
            cell.value = email_clean
            if "@" in email_clean:
                row[col_domain - 1].value = email_clean.split("@")[-1]
        # Phone
        if col_phone:
            cell = row[col_phone - 1]
            if isinstance(cell.value, str):
                cell.value = re.sub(r"[^\d]", "", cell.value)

def clean_data(wb, ws):
    headers = [cell.value for cell in ws[1]]

    try:
        col_first = headers.index("First Name") + 1
        col_last = headers.index("Last Name") + 1
        col_email = headers.index("Email Address") + 1
        col_domain = headers.index("Domain") + 1
        col_phone = headers.index("Phone Number") + 1 if "Phone Number" in headers else None
    except ValueError:
        raise Exception("Missing one or more required headers.")

    # Step 1: Clean all data generically (now faster)
    clean_all_data(ws)

    # Step 2: Format specific columns (already optimal)
    format_specific_columns(ws, col_first, col_last, col_email, col_domain, col_phone)

    return wb, ws
