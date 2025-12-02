# validators/same_client_validator.py

from utils.file_utils import disqualify_lead

def same_client_validator(wb, ws, suppressed_companies_input):
    # Convert input into list of lowercase suppressed names
    suppressed_companies = [
        name.strip().lower() for name in suppressed_companies_input.split(",") if name.strip()
    ]

    # Extract column headers and map to indices (1-based)
    headers = [cell.value.strip().lower() if cell.value else "" for cell in ws[1]]
    header_map = {header: idx + 1 for idx, header in enumerate(headers)}

    required = ["company name", "lead status", "dq reason", "qa comment"]
    for col in required:
        if col not in header_map:
            raise ValueError(f"Missing required column: {col}")

    col_company = header_map["company name"]
    col_status = header_map["lead status"]
    col_reason = header_map["dq reason"]
    col_comment = header_map["qa comment"]
    
    for row_num in range(2, ws.max_row + 1):
        company_cell = ws.cell(row=row_num, column=col_company)
        company_value = str(company_cell.value or "").lower()

        # Partial match check
        if any(supp_name in company_value for supp_name in suppressed_companies):
            disqualify_lead(
                ws, 
                row=row_num,
                col_status=col_status, 
                col_reason=col_reason, 
                col_comment=col_comment, 
                reason="Client Suppression", 
                comment="Same Company End Client"
            )
    return wb, ws
