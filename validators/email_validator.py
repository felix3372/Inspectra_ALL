from utils.file_utils import disqualify_lead
from utils.email_utils import generate_validation_patterns, strip_unicode  # ✅ Changed import

def validate_emails(wb, ws):
    headers = [cell.value for cell in ws[1]]

    try:
        col_first = headers.index("First Name") + 1
        col_last = headers.index("Last Name") + 1
        col_email = headers.index("Email Address") + 1
        col_domain = headers.index("Domain") + 1
        col_status = headers.index("Lead Status") + 1
        col_reason = headers.index("DQ Reason") + 1
        col_comment = headers.index("QA Comment") + 1
    except ValueError:
        raise Exception("Missing one or more required headers.")

    for row in range(2, ws.max_row + 1):
        # ✅ Normalize name and domain using the same logic as permutation generator
        first = strip_unicode(str(ws.cell(row, col_first).value or "").strip().lower())
        last = strip_unicode(str(ws.cell(row, col_last).value or "").strip().lower())
        domain = strip_unicode(str(ws.cell(row, col_domain).value or "").strip().lower())

        raw_email = str(ws.cell(row, col_email).value or "")
        email = ''.join(c for c in raw_email if c.isprintable()).strip().lower()
        email = email.replace(" ", "")

        if not all([first, last, email, domain]):
            disqualify_lead(
                ws, row,
                col_status=col_status,
                col_reason=col_reason,
                col_comment=col_comment,
                reason="Invalid Email",
                comment="Incorrect Email Format"
            )
            continue

        valid_patterns = generate_validation_patterns(first, last, domain)  # ✅ Changed function call

        if email not in valid_patterns:
            disqualify_lead(
                ws, row,
                col_status=col_status,
                col_reason=col_reason,
                col_comment=col_comment,
                reason="Invalid Email",
                comment="Incorrect Email Format"
            )

    return wb, ws