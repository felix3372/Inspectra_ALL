from collections import defaultdict
from .utils import normalize_company, ensure_col_in_ws
from utils.email_utils import extract_root_domain
from utils.file_utils import disqualify_lead

class DomainBasedChecker:
    """Enhanced CPC checker that uses root domain as primary company identifier"""
    
    def __init__(self, cpc_limit):
        self.cpc_limit = cpc_limit
        self.stats = {
            'cpc_violations': 0,
            'companies_checked': set(),
            'domains_checked': set(),
            'root_domains_checked': set(),  # Track root domains
            'domain_company_mapping': {}  # domain -> company name for reference
        }
    
    def get_company_identifier(self, row, company_col, domain_col):
        """Get the best company identifier - prioritize ROOT DOMAIN, fallback to company name"""
        domain = ""
        company = ""
        identifier = ""
        display_name = ""
        root_domain = ""
        
        # Extract domain and root domain
        if domain_col != "Not Available":
            domain_raw = str(row.get(domain_col, "")).strip().lower()
            if domain_raw:
                domain = domain_raw
                root_domain = extract_root_domain(domain_raw)
        
        # Extract company name
        if company_col != "Not Available":
            company_raw = str(row.get(company_col, "")).strip()
            if company_raw:
                company = normalize_company(company_raw)
        
        # Determine primary identifier and display name - PRIORITIZE ROOT DOMAIN
        if root_domain:
            identifier = f"root_domain:{root_domain}"
            display_name = f"{company} ({root_domain})" if company else root_domain
            # Store mapping for reference
            if root_domain not in self.stats['domain_company_mapping'] and company:
                self.stats['domain_company_mapping'][root_domain] = company
            self.stats['root_domains_checked'].add(root_domain)
        elif company:
            identifier = f"company:{company}"
            display_name = company
        
        return identifier, display_name, domain, company, root_domain
    
    def run_domain_based_cpc_check(self, delivery_data, lead_data, lead_ws, mapping, lead_headers):
        """Run CPC check using ROOT DOMAIN-based company identification"""
        
        # Count delivery occurrences by root domain/company
        delivery_counts = defaultdict(int)
        
        # Also maintain traditional counts for backward compatibility
        delivery_counts_traditional = {
            'company': defaultdict(int),
            'tal': defaultdict(int), 
            'domain': defaultdict(int),
            'root_domain': defaultdict(int)
        }
        
        # Process delivery data
        for drow in delivery_data:
            identifier, display_name, domain, company, root_domain = self.get_company_identifier(
                drow, 
                mapping.get('delivery_company', 'Not Available'),
                mapping.get('delivery_domain', 'Not Available')
            )
            
            if identifier:
                delivery_counts[identifier] += 1
                if domain:
                    self.stats['domains_checked'].add(domain)
                if company:
                    self.stats['companies_checked'].add(company)
            
            # Traditional counting for backward compatibility
            if mapping.get('delivery_company') != "Not Available":
                comp = company if company else ""
                if comp:
                    delivery_counts_traditional['company'][comp] += 1
            
            if mapping.get('delivery_tal') != "Not Available":
                tal_raw = str(drow.get(mapping.get('delivery_tal', ''), "")).strip()
                if tal_raw:
                    tal = normalize_company(tal_raw)
                    delivery_counts_traditional['tal'][tal] += 1
            
            if mapping.get('delivery_domain') != "Not Available":
                domain_raw = str(drow.get(mapping.get('delivery_domain', ''), "")).strip().lower()
                if domain_raw:
                    delivery_counts_traditional['domain'][domain_raw] += 1
                    root = extract_root_domain(domain_raw)
                    if root:
                        delivery_counts_traditional['root_domain'][root] += 1
        
        # Add enhanced columns with root domain focus
        cpc_primary_col = ensure_col_in_ws(lead_headers, lead_ws, "CPC by Root Domain Primary")
        cpc_breakdown_col = ensure_col_in_ws(lead_headers, lead_ws, "CPC Breakdown")
        
        # Traditional columns for backward compatibility
        cpc_company_col = ensure_col_in_ws(lead_headers, lead_ws, "CPC by Company Name")
        cpc_tal_col = ensure_col_in_ws(lead_headers, lead_ws, "CPC by TAL Company Name")
        cpc_domain_col = ensure_col_in_ws(lead_headers, lead_ws, "CPC by Domain")
        cpc_root_domain_col = ensure_col_in_ws(lead_headers, lead_ws, "CPC by Root Domain")
        
        # Get status columns
        lead_status_col = lead_headers.index("Lead Status") + 1
        dq_reason_col = lead_headers.index("DQ Reason") + 1
        qa_comment_col = lead_headers.index("QA Comment") + 1
        
        # Track lead counts
        lead_counts = defaultdict(int)
        lead_counts_traditional = {
            'company': defaultdict(int),
            'tal': defaultdict(int),
            'domain': defaultdict(int),
            'root_domain': defaultdict(int)
        }
        
        # Process each lead
        for idx, lrow in enumerate(lead_data, start=2):
            identifier, display_name, domain, company, root_domain = self.get_company_identifier(
                lrow,
                mapping.get('lead_company', 'Not Available'),
                mapping.get('lead_domain', 'Not Available')
            )
            
            # Traditional values for backward compatibility
            company_val = company if company else ""
            tal_val = ""
            domain_val = ""
            root_val = root_domain
            
            if mapping.get('lead_tal') != "Not Available":
                tal_raw = str(lrow.get(mapping.get('lead_tal', ''), "")).strip()
                if tal_raw:
                    tal_val = normalize_company(tal_raw)
            
            if mapping.get('lead_domain') != "Not Available":
                domain_raw = str(lrow.get(mapping.get('lead_domain', ''), "")).strip().lower()
                if domain_raw:
                    domain_val = domain_raw
                    if not root_val:  # Fallback if not set from get_company_identifier
                        root_val = extract_root_domain(domain_raw) or ""
            
            # Update counters
            if identifier:
                lead_counts[identifier] += 1
                if domain:
                    self.stats['domains_checked'].add(domain)
                if company:
                    self.stats['companies_checked'].add(company)
            
            # Traditional counting
            if company_val:
                lead_counts_traditional['company'][company_val] += 1
            if tal_val:
                lead_counts_traditional['tal'][tal_val] += 1
            if domain_val:
                lead_counts_traditional['domain'][domain_val] += 1
            if root_val:
                lead_counts_traditional['root_domain'][root_val] += 1
            
            # Calculate totals (prioritize root domain-based logic)
            total_count = delivery_counts[identifier] + lead_counts[identifier] if identifier else 0
            
            # Traditional totals
            company_total = (delivery_counts_traditional['company'].get(company_val, 0) + 
                           lead_counts_traditional['company'].get(company_val, 0)) if company_val else 0
            tal_total = (delivery_counts_traditional['tal'].get(tal_val, 0) + 
                       lead_counts_traditional['tal'].get(tal_val, 0)) if tal_val else 0
            domain_total = (delivery_counts_traditional['domain'].get(domain_val, 0) + 
                          lead_counts_traditional['domain'].get(domain_val, 0)) if domain_val else 0
            root_total = (delivery_counts_traditional['root_domain'].get(root_val, 0) + 
                        lead_counts_traditional['root_domain'].get(root_val, 0)) if root_val else 0
            
            # Write to enhanced columns (root domain focused)
            lead_ws.cell(idx, cpc_primary_col, total_count if total_count > 0 else "")
            
            # Create breakdown info
            if identifier:
                breakdown_info = f"{display_name}: {total_count}"
                if root_domain:
                    breakdown_info += f" (Root domain: {root_domain})"
                elif company:
                    breakdown_info += " (Company name-based)"
                lead_ws.cell(idx, cpc_breakdown_col, breakdown_info)
            
            # Traditional columns
            lead_ws.cell(idx, cpc_company_col, company_total if company_val else "")
            lead_ws.cell(idx, cpc_tal_col, tal_total if tal_val else "")
            lead_ws.cell(idx, cpc_domain_col, domain_total if domain_val else "")
            lead_ws.cell(idx, cpc_root_domain_col, root_total if root_val else "")
            
            # Check for violations - PRIORITIZE ROOT DOMAIN LOGIC
            violations = []
            
            # Primary violation check using root domain-based identifier
            if identifier and total_count > self.cpc_limit:
                if root_domain:
                    violation_msg = f"CPC Exceeded: Root Domain '{root_domain}' ({total_count}/{self.cpc_limit})"
                    if company:
                        violation_msg += f" - {company}"
                else:
                    violation_msg = f"CPC Exceeded: {display_name} ({total_count}/{self.cpc_limit})"
                violations.append(violation_msg)
            
            # Additional traditional violations (only if not already caught by primary check)
            if not violations:
                if company_val and company_total > self.cpc_limit:
                    violations.append(f"CPC Exceeded by Company Name ({company_total}/{self.cpc_limit})")
                if tal_val and tal_total > self.cpc_limit:
                    violations.append(f"CPC Exceeded by TAL Company Name ({tal_total}/{self.cpc_limit})")
                if root_val and root_total > self.cpc_limit:
                    violations.append(f"CPC Exceeded by Root Domain '{root_val}' ({root_total}/{self.cpc_limit})")
                elif domain_val and domain_total > self.cpc_limit:
                    violations.append(f"CPC Exceeded by Exact Domain ({domain_total}/{self.cpc_limit})")
            
            # Disqualify if violations found
            if violations:
                # Remove duplicates and use the most relevant violation
                unique_violations = list(set(violations))
                disqualify_lead(
                    lead_ws, idx,
                    col_status=lead_status_col,
                    col_reason=dq_reason_col,
                    col_comment=qa_comment_col,
                    reason="Extra CPC",
                    comment="; ".join(unique_violations[:2])  # Limit to first 2 to avoid overly long comments
                )
                self.stats['cpc_violations'] += 1
        
        return self.stats
    
    def get_domain_analysis(self):
        """Get analysis of domains and their associated companies"""
        analysis = {
            'total_domains': len(self.stats['domains_checked']),
            'total_root_domains': len(self.stats['root_domains_checked']),
            'total_companies': len(self.stats['companies_checked']),
            'domain_company_mapping': self.stats['domain_company_mapping'],
            'domains_list': sorted(list(self.stats['domains_checked'])),
            'root_domains_list': sorted(list(self.stats['root_domains_checked'])),
            'companies_list': sorted(list(self.stats['companies_checked']))
        }
        return analysis