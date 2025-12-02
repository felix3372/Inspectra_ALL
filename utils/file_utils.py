import io
import csv
import pycountry


def disqualify_lead(ws, row, col_status, col_reason, col_comment, reason, comment):
    # Set status and reason only if not already filled
    if not ws.cell(row, col_status).value:
        ws.cell(row, col_status).value = "Disqualified"
    if not ws.cell(row, col_reason).value:
        ws.cell(row, col_reason).value = reason

    # Always append to QA comment
    existing_comment = str(ws.cell(row, col_comment).value or "").strip()
    if comment not in existing_comment:
        if existing_comment:
            ws.cell(row, col_comment).value = f"{existing_comment}, {comment}"
        else:
            ws.cell(row, col_comment).value = comment



def build_pycountry_csv() -> bytes:
    """
    Generates a CSV of acceptable country names from pycountry (ISO 3166).
    Columns: alpha_2, alpha_3, name, official_name, common_name
    Returns bytes for direct use in a Streamlit download_button.
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["alpha_2", "alpha_3", "name", "official_name", "common_name"])
    
    for c in pycountry.countries:
        alpha2 = getattr(c, "alpha_2", "") or ""
        alpha3 = getattr(c, "alpha_3", "") or ""
        name = getattr(c, "name", "") or ""
        official = getattr(c, "official_name", "") if hasattr(c, "official_name") else ""
        common = getattr(c, "common_name", "") if hasattr(c, "common_name") else ""
        writer.writerow([alpha2, alpha3, name, official, common])
    
    return buf.getvalue().encode("utf-8")
