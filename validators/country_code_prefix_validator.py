import re
from utils.country_dial_codes import COUNTRY_DIAL_CODES

def is_valid_us_ca_number(digits):
    # Only accept 10 or 11 digits
    if len(digits) == 11:
        # Must start with '1' and then digit 2-9
        return digits.startswith("1") and digits[1] in "23456789"
    elif len(digits) == 10:
        # Must start with digit 2-9
        return digits[0] in "23456789"
    return False  # Invalid length

def starts_with_country_code(phone, country):
    digits = re.sub(r"[^\d]", "", str(phone or ""))
    country_key = str(country or "").strip().lower()
    code = COUNTRY_DIAL_CODES.get(country_key)
    if not code:
        # If country not in mapping, skip validation
        return True
    if country_key in ("united states", "canada"):
        return is_valid_us_ca_number(digits)
    # For other countries, must start with country code
    return digits.startswith(code)

def country_code_validator(wb, ws):
    headers = [str(cell.value or "").strip().lower() for cell in ws[1]]
    required_cols = {"phone number", "country", "lead status", "dq reason", "qa comment"}
    if not required_cols.issubset(set(headers)):
        return wb, ws

    col_phone = headers.index("phone number") + 1
    col_country = headers.index("country") + 1
    col_status = headers.index("lead status") + 1
    col_reason = headers.index("dq reason") + 1
    col_comment = headers.index("qa comment") + 1

    for row in range(2, ws.max_row + 1):
        phone = ws.cell(row, col_phone).value
        country = ws.cell(row, col_country).value
        if phone and country and not starts_with_country_code(phone, country):
            from utils.file_utils import disqualify_lead
            country_key = str(country).strip().lower()
            if country_key in ("united states", "canada"):
                comment_msg = "Phone number does not start with country code or invalid US/Canada format"
            else:
                comment_msg = "Phone number does not start with the valid country code"

            disqualify_lead(
                ws, row,
                col_status,
                col_reason,
                col_comment,
                reason="Invalid Phone Number",
                comment=comment_msg
            )
    return wb, ws
