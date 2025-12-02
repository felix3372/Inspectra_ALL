import re
import difflib
import unicodedata
import tldextract  # Make sure this is installed

def strip_unicode(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def clean_company_name(name):
    name = strip_unicode(name.lower())
    name = re.sub(r"[^a-z0-9 ]", " ", name)  # remove punctuation, keep space
    blacklist = {"inc", "llc", "ltd", "co", "corp", "corporation", "gmbh", "plc", "limited", "pte", "the"}
    words = [w for w in name.split() if w not in blacklist and len(w) > 1]
    return words

def clean_domain(domain):
    domain = domain.lower()
    domain = strip_unicode(domain)
    domain = re.sub(r"https?://", "", domain)
    domain = re.sub(r"[^a-z0-9.]", "", domain)
    ext = tldextract.extract(domain)
    return ext.top_domain_under_public_suffix or domain


def company_initials(words):
    return ''.join(w[0] for w in words if w)

def validate_company_domain_match(wb, ws):
    headers = [cell.value for cell in ws[1]]

    try:
        col_company = headers.index("Company Name") + 1
        col_domain = headers.index("Domain") + 1
    except ValueError:
        return wb, ws  # Required columns not present

    if "Domain Validation" in headers:
        col_comment = headers.index("Domain Validation") + 1
    else:
        col_comment = len(headers) + 1
        ws.cell(row=1, column=col_comment).value = "Domain Validation"

    domain_exceptions = {
        "alphabet": ["google"],
        "international business machines": ["ibm"],
        "procter gamble": ["pg"],
        "united parcel service": ["ups"],
        # ...add more known aliases as needed
    }

    for row in range(2, ws.max_row + 1):
        company = str(ws.cell(row, col_company).value or "").strip()
        domain = str(ws.cell(row, col_domain).value or "").strip()

        if not company or not domain:
            continue

        keywords = clean_company_name(company)
        root_domain = clean_domain(domain)

        # 1. Direct match of keywords
        if any(kw in root_domain for kw in keywords):
            continue

        # 2. Fuzzy partial match for each keyword
        for kw in keywords:
            if difflib.SequenceMatcher(None, kw, root_domain).ratio() >= 0.80:
                break
        else:
            initials = company_initials(keywords)
            if initials and initials in root_domain:
                continue

            normalized_company = ' '.join(keywords)
            for k, vals in domain_exceptions.items():
                if k in normalized_company:
                    if any(val in root_domain for val in vals):
                        break
            else:
                ws.cell(row, col_comment).value = "Company name-domain mismatch"

    return wb, ws
