"""
Duplicate Header Validator
Checks if any of the required headers appear more than once in the uploaded file.
"""

def validate_duplicate_headers(ws):
    """
    Validates that none of the required headers appear multiple times in the worksheet.
    Only checks required headers, not all columns.
    
    Args:
        ws: openpyxl worksheet object
    
    Raises:
        ValueError: If any required header appears more than once
    """
    
    # Define required headers (same as header_validator.py)
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
    
    # Get all headers from the worksheet (normalized to lowercase)
    headers_in_sheet = []
    original_headers = []  # Keep track of original case
    
    for cell in ws[1]:
        if cell.value:
            original_headers.append(str(cell.value).strip())
            headers_in_sheet.append(str(cell.value).strip().lower())
    
    # Check each required header for duplicates
    duplicates = {}
    
    for req_header in required_headers:
        # Count how many times this required header appears
        count = headers_in_sheet.count(req_header)
        
        if count > 1:
            # Find positions where this header appears
            positions = []
            originals = []
            for i, h in enumerate(headers_in_sheet):
                if h == req_header:
                    positions.append(i + 1)  # 1-indexed column numbers
                    originals.append(original_headers[i])
            
            duplicates[req_header] = {
                'count': count,
                'positions': positions,
                'originals': originals
            }
    
    # If duplicates found, raise error with details
    if duplicates:
        error_lines = ["❌ DUPLICATE REQUIRED HEADERS DETECTED"]
        error_lines.append("\nThe following required headers appear multiple times in your file:")
        error_lines.append("")
        
        for header, info in duplicates.items():
            error_lines.append(f"  🔴 '{header.title()}' appears {info['count']} times:")
            for i, (pos, orig) in enumerate(zip(info['positions'], info['originals']), 1):
                error_lines.append(f"     {i}. Column {pos}: '{orig}'")
            error_lines.append("")
        
        error_lines.append("="*80)
        error_lines.append("💡 SOLUTION:")
        error_lines.append("Please ensure each required header appears only ONCE in your file.")
        error_lines.append("Remove or rename the duplicate columns before uploading.")
        error_lines.append("="*80)
        
        error_message = "\n".join(error_lines)
        raise ValueError(error_message)
    
    # If no duplicates, validation passes
    return True