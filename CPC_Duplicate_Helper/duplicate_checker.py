from utils.email_utils import generate_email_permutations
from utils.file_utils import disqualify_lead

class DuplicateChecker:
    """Handle duplicate detection across files and internally"""
    
    def __init__(self):
        self.stats = {
            'duplicates_found': 0,
            'internal_duplicates': 0,
            'permutation_errors': 0,
            'duplicate_details': []
        }
    
    def run_duplicate_check(self, delivery_data, lead_data, lead_ws, mapping, 
                          lead_status_col, dq_reason_col, qa_comment_col):
        """Run complete duplicate check process"""
        
        # Build delivery signatures
        delivery_signatures = self._build_delivery_signatures(delivery_data, mapping)
        
        # Check lead file for duplicates
        lead_signatures = {'emails': set(), 'linkedin': set()}
        
        for idx, lrow in enumerate(lead_data, start=2):
            # Skip if already disqualified
            if lead_ws.cell(idx, lead_status_col).value == "Disqualified":
                continue

            duplicate_found = False
            duplicate_reasons = []
            
            # Extract values
            email_val = (lrow.get(mapping.get('lead_email', ''), "")).strip().lower() if mapping.get('lead_email') != "Not Available" else ""
            linkedin_val = (lrow.get(mapping.get('lead_linkedin', ''), "")).strip().lower() if mapping.get('lead_linkedin') != "Not Available" else ""

            # Check against delivery file
            if email_val and email_val in delivery_signatures['emails']:
                duplicate_found = True
                duplicate_reasons.append("Email match in delivery")
                self.stats['duplicate_details'].append({
                    'row': idx,
                    'type': 'email',
                    'value': email_val
                })
            
            if linkedin_val and linkedin_val in delivery_signatures['linkedin']:
                duplicate_found = True
                duplicate_reasons.append("LinkedIn match in delivery")
                self.stats['duplicate_details'].append({
                    'row': idx,
                    'type': 'linkedin', 
                    'value': linkedin_val
                })

            # Check email permutations
            if not duplicate_found and self._can_check_permutations(mapping):
                lf = (lrow.get(mapping.get('lead_first', ''), "")).strip()
                ll = (lrow.get(mapping.get('lead_last', ''), "")).strip()
                ld = (lrow.get(mapping.get('lead_domain', ''), "")).strip()
                
                if lf and ll and ld:
                    try:
                        perms_lead = generate_email_permutations(lf, ll, ld)
                        if perms_lead & delivery_signatures['email_permutations']:
                            duplicate_found = True
                            duplicate_reasons.append("Email permutation match in delivery")
                            self.stats['duplicate_details'].append({
                                'row': idx,
                                'type': 'permutation',
                                'value': f"{lf} {ll} @ {ld}"
                            })
                    except Exception:
                        self.stats['permutation_errors'] += 1

            # Internal duplicate check
            internal_duplicate = False
            if email_val and email_val in lead_signatures['emails']:
                internal_duplicate = True
                duplicate_reasons.append("Internal duplicate email")
            if linkedin_val and linkedin_val in lead_signatures['linkedin']:
                internal_duplicate = True
                duplicate_reasons.append("Internal duplicate LinkedIn")

            # Add to lead signatures for future internal checks
            if email_val:
                lead_signatures['emails'].add(email_val)
            if linkedin_val:
                lead_signatures['linkedin'].add(linkedin_val)

            # Disqualify if duplicates found
            if duplicate_found:
                disqualify_lead(
                    lead_ws, idx,
                    col_status=lead_status_col,
                    col_reason=dq_reason_col,
                    col_comment=qa_comment_col,
                    reason="Same Prospect Duplicate",
                    comment="Same Prospect Same Campaign - " + "; ".join(duplicate_reasons)
                )
                self.stats['duplicates_found'] += 1
            elif internal_duplicate:
                disqualify_lead(
                    lead_ws, idx,
                    col_status=lead_status_col,
                    col_reason=dq_reason_col,
                    col_comment=qa_comment_col,
                    reason="Internal Duplicate",
                    comment="Duplicate within file - " + "; ".join(duplicate_reasons)
                )
                self.stats['internal_duplicates'] += 1

        return self.stats
    
    def _build_delivery_signatures(self, delivery_data, mapping):
        """Build signature sets from delivery data"""
        delivery_signatures = {
            'emails': set(),
            'email_permutations': set(),
            'linkedin': set()
        }

        for drow in delivery_data:
            # Email signatures
            if mapping.get('delivery_email') != "Not Available":
                e = (drow.get(mapping.get('delivery_email', ''), "")).strip().lower()
                if e:
                    delivery_signatures['emails'].add(e)
            
            # Email permutations
            if self._can_check_permutations(mapping):
                f = (drow.get(mapping.get('delivery_first', ''), "")).strip()
                l = (drow.get(mapping.get('delivery_last', ''), "")).strip()
                d = (drow.get(mapping.get('delivery_domain', ''), "")).strip()
                
                if f and l and d:
                    try:
                        perms = generate_email_permutations(f, l, d)
                        delivery_signatures['email_permutations'].update(perms)
                    except Exception:
                        self.stats['permutation_errors'] += 1
            
            # LinkedIn signatures
            if mapping.get('delivery_linkedin') != "Not Available":
                li = (drow.get(mapping.get('delivery_linkedin', ''), "")).strip().lower()
                if li:
                    delivery_signatures['linkedin'].add(li)

        return delivery_signatures
    
    def _can_check_permutations(self, mapping):
        """Check if permutation checking is possible with current mapping"""
        return (mapping.get('delivery_first') != "Not Available" and
                mapping.get('delivery_last') != "Not Available" and
                mapping.get('delivery_domain') != "Not Available" and
                mapping.get('lead_first') != "Not Available" and
                mapping.get('lead_last') != "Not Available" and
                mapping.get('lead_domain') != "Not Available")