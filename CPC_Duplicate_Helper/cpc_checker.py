from collections import defaultdict
from .utils import normalize_company, ensure_col_in_ws
from utils.email_utils import extract_root_domain
from utils.file_utils import disqualify_lead

class CPCChecker:
    """Handle CPC (Contact Per Company) validation"""
    
    def __init__(self, cpc_limit):
        self.cpc_limit = cpc_limit
        self.stats = {
            'cpc_violations': 0,
            'companies_checked': set()
        }
    
    def run_cpc_check(self, delivery_data, lead_data, lead_ws, mapping, lead_headers):
        """Run complete CPC check process with root domain priority"""
        
        # Count delivery occurrences
        delivery_counts = self._count_delivery_occurrences(delivery_data, mapping)
        
        # Add CPC columns to lead file
        cpc_company_col = ensure_col_in_ws(lead_headers, lead_ws, "CPC by Company Name")
        cpc_tal_col = ensure_col_in_ws(lead_headers, lead_ws, "CPC by TAL Company Name")
        cpc_domain_col = ensure_col_in_ws(lead_headers, lead_ws, "CPC by Domain")
        cpc_root_domain_col = ensure_col_in_ws(lead_headers, lead_ws, "CPC by Root Domain")
        
        # Get column indices for status tracking
        lead_status_col = lead_headers.index("Lead Status") + 1
        dq_reason_col = lead_headers.index("DQ Reason") + 1
        qa_comment_col = lead_headers.index("QA Comment") + 1
        
        # Track lead counts
        lead_counts = {
            'company': defaultdict(int),
            'tal': defaultdict(int),
            'domain': defaultdict(int),
            'root_domain': defaultdict(int)
        }

        # Process each lead
        for idx, lrow in enumerate(lead_data, start=2):
            violations = []
            
            # Extract values
            company_val = normalize_company(lrow.get(mapping.get('lead_company', ''), "")) if mapping.get('lead_company') != "Not Available" else ""
            tal_val = normalize_company(lrow.get(mapping.get('lead_tal', ''), "")) if mapping.get('lead_tal') != "Not Available" else ""
            domain_val = (lrow.get(mapping.get('lead_domain', ''), "")).strip().lower() if mapping.get('lead_domain') != "Not Available" else ""
            root_val = extract_root_domain(domain_val) if domain_val else ""

            # Track companies
            if company_val:
                lead_counts['company'][company_val] += 1
                self.stats['companies_checked'].add(company_val)
            if tal_val:
                lead_counts['tal'][tal_val] += 1
            if domain_val:
                lead_counts['domain'][domain_val] += 1
            if root_val:
                lead_counts['root_domain'][root_val] += 1

            # Calculate totals
            company_total = (delivery_counts['company'].get(company_val, 0) + 
                           lead_counts['company'].get(company_val, 0)) if company_val else 0
            tal_total = (delivery_counts['tal'].get(tal_val, 0) + 
                       lead_counts['tal'].get(tal_val, 0)) if tal_val else 0
            domain_total = (delivery_counts['domain'].get(domain_val, 0) + 
                          lead_counts['domain'].get(domain_val, 0)) if domain_val else 0
            root_total = (delivery_counts['root_domain'].get(root_val, 0) + 
                        lead_counts['root_domain'].get(root_val, 0)) if root_val else 0

            # Write counts to worksheet
            lead_ws.cell(idx, cpc_company_col, company_total if company_val else "")
            lead_ws.cell(idx, cpc_tal_col, tal_total if tal_val else "")
            lead_ws.cell(idx, cpc_domain_col, domain_total if domain_val else "")
            lead_ws.cell(idx, cpc_root_domain_col, root_total if root_val else "")

            # Check violations - PRIORITIZE ROOT DOMAIN
            if company_val and company_total > self.cpc_limit:
                violations.append(f"CPC Exceeded by Company Name ({company_total}/{self.cpc_limit})")
            if tal_val and tal_total > self.cpc_limit:
                violations.append(f"CPC Exceeded by TAL Company Name ({tal_total}/{self.cpc_limit})")
            
            # For domain violations, prioritize root domain over exact domain
            if root_val and root_total > self.cpc_limit:
                violations.append(f"CPC Exceeded by Root Domain '{root_val}' ({root_total}/{self.cpc_limit})")
            elif domain_val and domain_total > self.cpc_limit:
                violations.append(f"CPC Exceeded by Exact Domain ({domain_total}/{self.cpc_limit})")

            # Disqualify if violations found
            if violations:
                disqualify_lead(
                    lead_ws, idx,
                    col_status=lead_status_col,
                    col_reason=dq_reason_col,
                    col_comment=qa_comment_col,
                    reason="Extra CPC",
                    comment="; ".join(violations)
                )
                self.stats['cpc_violations'] += 1

        return self.stats
    
    def _count_delivery_occurrences(self, delivery_data, mapping):
        """Count occurrences in delivery file with enhanced root domain tracking"""
        delivery_counts = {
            'company': defaultdict(int),
            'tal': defaultdict(int),
            'domain': defaultdict(int),
            'root_domain': defaultdict(int)
        }

        for drow in delivery_data:
            # Company counting
            if mapping.get('delivery_company') != "Not Available":
                comp = normalize_company(drow.get(mapping.get('delivery_company', ''), ""))
                if comp:
                    delivery_counts['company'][comp] += 1
            
            # TAL counting
            if mapping.get('delivery_tal') != "Not Available":
                tal = normalize_company(drow.get(mapping.get('delivery_tal', ''), ""))
                if tal:
                    delivery_counts['tal'][tal] += 1
            
            # Domain counting - both exact and root
            if mapping.get('delivery_domain') != "Not Available":
                dom = (drow.get(mapping.get('delivery_domain', ''), "")).strip().lower()
                if dom:
                    delivery_counts['domain'][dom] += 1
                    # Always extract root domain for better CPC checking
                    root = extract_root_domain(dom)
                    if root:
                        delivery_counts['root_domain'][root] += 1

        return delivery_counts