def validate_required_headers(ws):
    required_headers = {
        "lead status",
        "dq reason",
        "qa comment",
        "first name",
        "last name",
        "email address",
        "domain",
        "job title",
        "company name",
        "phone number",
        "job level",
        "revenue size",
        "linkedin link prospect",
        "company linkedin link",
        "time-stamp"
    }

    # Normalize headers from first row
    headers_in_sheet = {
        str(cell.value).strip().lower() for cell in ws[1] if cell.value
    }

    missing_headers = sorted(required_headers - headers_in_sheet)

    if missing_headers:
        raise ValueError(
            "❌ Missing required header(s):\n\n" + "\n".join(f"- {h.title()}" for h in missing_headers)
        )
