import re
from utils.tollfree_prefixes import TOLLFREE_PREFIXES
from utils.country_dial_codes import COUNTRY_DIAL_CODES
from utils.file_utils import disqualify_lead


def is_tollfree_number(phone, country):
    if phone is None:
        return False
    phone_str = str(phone)
    country_key = str(country or "").strip().lower()
    prefixes = TOLLFREE_PREFIXES.get(country_key, [])
    country_code = COUNTRY_DIAL_CODES.get(country_key, "")
    # Remove country code prefix if present
    if country_code and phone_str.startswith(country_code):
        phone_str = phone_str[len(country_code):]
    return any(phone_str.startswith(prefix) for prefix in prefixes)

def tollfree_validator(wb, ws):
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

        if phone and country and is_tollfree_number(phone, country):
            disqualify_lead(
                ws, row,
                col_status,
                col_reason,
                col_comment,
                reason="Toll Free Number",
                comment="Phone number is toll-free"
            )
    return wb, ws
