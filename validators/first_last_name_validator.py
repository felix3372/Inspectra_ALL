from utils.file_utils import disqualify_lead

def first_last_name_validator(wb, ws, debug=False):
    headers = [cell.value for cell in ws[1]]
    
    try:
        col_first = headers.index("First Name") + 1
        col_last = headers.index("Last Name") + 1
        col_status = headers.index("Lead Status") + 1
        col_reason = headers.index("DQ Reason") + 1
        col_comment = headers.index("QA Comment") + 1
    except ValueError:
        raise Exception("Missing one or more required headers.")
        
    for row in range(2, ws.max_row + 1):
        first = str(ws.cell(row, col_first).value or "").strip()
        last = str(ws.cell(row, col_last).value or "").strip()
        
        # Convert to lowercase for case-insensitive comparisons
        first_lower = first.lower()
        last_lower = last.lower()
        
        # Check for single character first name
        if len(first) == 1:
            disqualify_lead(
                ws, row,
                col_status=col_status,
                col_reason=col_reason,
                col_comment=col_comment,
                reason="Invalid Details",
                comment="First Name Initial Not Allowed"
            )
                
        # Check for single character last name
        elif len(last) == 1:
            disqualify_lead(
                ws, row,
                col_status=col_status,
                col_reason=col_reason,
                col_comment=col_comment,
                reason="Invalid Details",
                comment="Last Name Initial Not allowed"
            )
                
        # Check for identical first and last names
        elif first_lower == last_lower and first:
            disqualify_lead(
                ws, row,
                col_status=col_status,
                col_reason=col_reason,
                col_comment=col_comment,
                reason="Invalid Details",
                comment="First/Last Name Same"
            )
                
        # NEW CHECK: First name contains last name (e.g., "John Davis" contains "Davis")
        # Only add QA comment, don't disqualify
        elif last_lower in first_lower and len(last) > 1:
            # Just add QA comment without disqualifying
            ws.cell(row, col_comment).value = "First Name Contains Last Name"
                
        # NEW CHECK: Last name contains first name (e.g., "Davis" contains "John" - though this example wouldn't trigger)
        # Better example: First: "John", Last: "Johnson" 
        # Only add QA comment, don't disqualify
        elif first_lower in last_lower and len(first) > 1:
            # Just add QA comment without disqualifying
            ws.cell(row, col_comment).value = "Last Name Contains First Name"
                
    return wb, ws