import tldextract
import unicodedata
import re
from utils.tld_country_domain_map import tld_country_map
from utils.file_utils import disqualify_lead  # Import your existing disqualify_lead

def strip_unicode(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def suffix_to_country(suffix):
    # Try full suffix, then right-most part (e.g., "co.jp" → "jp")
    return tld_country_map.get(suffix, tld_country_map.get(suffix.split('.')[-1], ""))

def clean_domain(domain):
    domain = domain.lower()
    domain = strip_unicode(domain)
    domain = re.sub(r"https?://", "", domain)
    domain = re.sub(r"[^a-z0-9.]", "", domain)
    ext = tldextract.extract(domain)
    return ext.top_domain_under_public_suffix or domain, ext.suffix

def domain_country_validator(wb, ws):
    headers = [cell.value for cell in ws[1]]

    try:
        col_domain = headers.index("Domain") + 1
        col_country = headers.index("Country") + 1
        col_status = headers.index("Lead Status") + 1
        col_reason = headers.index("DQ Reason") + 1
        col_comment = headers.index("QA Comment") + 1
    except ValueError:
        return wb, ws

    for row in range(2, ws.max_row + 1):
        domain = str(ws.cell(row, col_domain).value or "").strip()
        country = str(ws.cell(row, col_country).value or "").strip()

        if not domain or not country:
            continue

        _, suffix = clean_domain(domain)
        domain_country = suffix_to_country(suffix)

        # If the domain country is found and does not match the listed country
        if domain_country and domain_country.lower() != country.lower():
            reason = "Invalid Email"
            comment = f"Email Domain suffix country ({domain_country}) does not match targeted country ({country})"
            disqualify_lead(
                ws, row,
                col_status=col_status,
                col_reason=col_reason,
                col_comment=col_comment,
                reason=reason,
                comment=comment
            )

    return wb, ws