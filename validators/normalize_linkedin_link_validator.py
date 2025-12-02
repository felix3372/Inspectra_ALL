# validators/normalize_linkedin_link_validator.py

def normalize_linkedin_link_validator(wb, ws):
    """
    Normalizes the 'Linkedin Link Prospect' column to the format:
    https://www.linkedin.com/in/{profile-id}/
    """

    headers = [str(cell.value).strip().lower() for cell in ws[1]]

    try:
        col_index = headers.index("linkedin link prospect") + 1
    except ValueError:
        raise Exception("❌ 'Linkedin Link Prospect' column not found.")

    for row in ws.iter_rows(min_row=2):
        cell = row[col_index - 1]
        link = str(cell.value or "").strip()

        if not link:
            continue

        # Step 1: Extract just the "/in/..." portion (cut after domain)
        if "/in/" not in link:
            continue  # not a valid LinkedIn profile link

        try:
            profile_part = link.split("/in/")[1].split("?")[0].strip("/")
            normalized = f"https://www.linkedin.com/in/{profile_part}/"
            cell.value = normalized
        except Exception:
            continue  # skip any malformed URLs

    return wb, ws