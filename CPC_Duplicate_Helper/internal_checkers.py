from collections import defaultdict
import re
from .utils import normalize_company, ensure_col_in_ws
from utils.email_utils import extract_root_domain, generate_email_permutations
from utils.file_utils import disqualify_lead


def normalize_linkedin_url(link):
    """
    Normalize a single LinkedIn URL string to standard format
    Based on the logic from validators/normalize_linkedin_link_validator.py
    """
    if not link:
        return ""
    
    link = str(link).strip()
    
    # Extract just the "/in/..." portion (cut after domain)
    if "/in/" not in link:
        return link.lower()  # not a valid LinkedIn profile link, return as-is
    
    try:
        profile_part = link.split("/in/")[1].split("?")[0].strip("/")
        normalized = f"https://www.linkedin.com/in/{profile_part}/"
        return normalized
    except Exception:
        return link.lower()  # fallback to lowercase if parsing fails

class InternalCPCChecker:
    """Handle internal CPC (Contact Per Company) validation within a single file with root domain priority"""
    
    def __init__(self, cpc_limit):
        self.cpc_limit = cpc_limit
        self.stats = {
            'internal_cpc_violations': 0,
            'internal_companies_checked': set(),
            'internal_root_domains_checked': set()
        }
    
    def run_internal_cpc_check(self, lead_data, lead_ws, mapping, lead_headers):
        """Run CPC check within the lead file only with ROOT DOMAIN PRIORITY"""
        
        # Add internal CPC columns
        internal_cpc_company_col = ensure_col_in_ws(lead_headers, lead_ws, "Internal CPC by Company")
        internal_cpc_tal_col = ensure_col_in_ws(lead_headers, lead_ws, "Internal CPC by TAL Company")
        internal_cpc_domain_col = ensure_col_in_ws(lead_headers, lead_ws, "Internal CPC by Domain")
        internal_cpc_root_col = ensure_col_in_ws(lead_headers, lead_ws, "Internal CPC by Root Domain")
        
        # Get column indices for status tracking
        lead_status_col = lead_headers.index("Lead Status") + 1
        dq_reason_col = lead_headers.index("DQ Reason") + 1
        qa_comment_col = lead_headers.index("QA Comment") + 1
        
        # Track internal counts
        internal_counts = {
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
            
            # Increment counts
            if company_val:
                internal_counts['company'][company_val] += 1
                self.stats['internal_companies_checked'].add(company_val)
            if tal_val:
                internal_counts['tal'][tal_val] += 1
            if domain_val:
                internal_counts['domain'][domain_val] += 1
            if root_val:
                internal_counts['root_domain'][root_val] += 1
                self.stats['internal_root_domains_checked'].add(root_val)
            
            # Get current counts
            company_count = internal_counts['company'].get(company_val, 0) if company_val else 0
            tal_count = internal_counts['tal'].get(tal_val, 0) if tal_val else 0
            domain_count = internal_counts['domain'].get(domain_val, 0) if domain_val else 0
            root_count = internal_counts['root_domain'].get(root_val, 0) if root_val else 0
            
            # Write counts to worksheet
            lead_ws.cell(idx, internal_cpc_company_col, company_count if company_val else "")
            lead_ws.cell(idx, internal_cpc_tal_col, tal_count if tal_val else "")
            lead_ws.cell(idx, internal_cpc_domain_col, domain_count if domain_val else "")
            lead_ws.cell(idx, internal_cpc_root_col, root_count if root_val else "")
            
            # Check violations - PRIORITIZE ROOT DOMAIN
            if company_val and company_count > self.cpc_limit:
                violations.append(f"Internal CPC Exceeded by Company ({company_count}/{self.cpc_limit})")
            if tal_val and tal_count > self.cpc_limit:
                violations.append(f"Internal CPC Exceeded by TAL Company ({tal_count}/{self.cpc_limit})")
            
            # For domain violations, prioritize root domain over exact domain
            if root_val and root_count > self.cpc_limit:
                violations.append(f"Internal CPC Exceeded by Root Domain '{root_val}' ({root_count}/{self.cpc_limit})")
            elif domain_val and domain_count > self.cpc_limit:
                violations.append(f"Internal CPC Exceeded by Exact Domain ({domain_count}/{self.cpc_limit})")
            
            # Disqualify if violations found
            if violations:
                disqualify_lead(
                    lead_ws, idx,
                    col_status=lead_status_col,
                    col_reason=dq_reason_col,
                    col_comment=qa_comment_col,
                    reason="Internal CPC Exceeded",
                    comment="; ".join(violations)
                )
                self.stats['internal_cpc_violations'] += 1
        
        return self.stats


class InternalDuplicateChecker:
    """Handle duplicate detection within a single file"""
    
    def __init__(self):
        self.stats = {
            'internal_duplicates': 0,
            'internal_duplicate_details': []
        }
    
    def run_internal_duplicate_check(self, lead_data, lead_ws, mapping, lead_status_col, dq_reason_col, qa_comment_col):
        """Check for duplicates within the lead file using conservative logic to avoid false positives"""
        
        # Track signatures within the file
        seen_signatures = {
            'emails': set(),
            'linkedin': set(),
            'name_domain_combinations': set()  # More conservative than full permutations
        }
        
        # Process each lead
        for idx, lrow in enumerate(lead_data, start=2):
            # Skip if already disqualified
            if lead_ws.cell(idx, lead_status_col).value == "Disqualified":
                continue
            
            duplicate_found = False
            duplicate_reasons = []
            
            # Extract values
            email_val = (lrow.get(mapping.get('lead_email', ''), "")).strip().lower() if mapping.get('lead_email') != "Not Available" else ""
            linkedin_raw = (lrow.get(mapping.get('lead_linkedin', ''), "")).strip() if mapping.get('lead_linkedin') != "Not Available" else ""
            
            # Normalize LinkedIn URL
            linkedin_val = ""
            if linkedin_raw:
                try:
                    linkedin_val = normalize_linkedin_url(linkedin_raw)
                except:
                    linkedin_val = linkedin_raw.lower()  # Fallback if normalization fails
            
            # Check email duplicates (exact match only)
            if email_val and email_val in seen_signatures['emails']:
                duplicate_found = True
                duplicate_reasons.append("Internal duplicate email")
                self.stats['internal_duplicate_details'].append({
                    'row': idx,
                    'type': 'email',
                    'value': email_val
                })
            
            # Check LinkedIn duplicates
            if linkedin_val and linkedin_val in seen_signatures['linkedin']:
                duplicate_found = True
                duplicate_reasons.append("Internal duplicate LinkedIn")
                self.stats['internal_duplicate_details'].append({
                    'row': idx,
                    'type': 'linkedin',
                    'value': linkedin_val
                })
            
            # Conservative name+domain checking (avoid false positives)
            if not duplicate_found and self._can_check_name_domain(mapping):
                first_name = (lrow.get(mapping.get('lead_first', ''), "")).strip().lower()
                last_name = (lrow.get(mapping.get('lead_last', ''), "")).strip().lower()
                domain_raw = (lrow.get(mapping.get('lead_domain', ''), "")).strip().lower()
                
                # Use ROOT DOMAIN for name+domain matching to catch variations
                domain = extract_root_domain(domain_raw) if domain_raw else domain_raw
                
                if first_name and last_name and domain:
                    # Create conservative signatures that require more exact matching
                    conservative_signatures = self._generate_conservative_name_signatures(first_name, last_name, domain)
                    
                    # Check if any conservative signature already exists
                    for signature in conservative_signatures:
                        if signature in seen_signatures['name_domain_combinations']:
                            duplicate_found = True
                            duplicate_reasons.append("Internal duplicate name+root domain match")
                            self.stats['internal_duplicate_details'].append({
                                'row': idx,
                                'type': 'name_root_domain',
                                'value': signature
                            })
                            break
                    
                    # Add signatures to seen set
                    seen_signatures['name_domain_combinations'].update(conservative_signatures)
            
            # Add to seen signatures
            if email_val:
                seen_signatures['emails'].add(email_val)
            if linkedin_val:
                seen_signatures['linkedin'].add(linkedin_val)
            
            # Disqualify if duplicate found
            if duplicate_found:
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
    
    def _generate_conservative_name_signatures(self, first_name, last_name, domain):
        """Generate conservative name signatures that avoid false positives like Jonathan Kyle vs Kyle Fleming"""
        signatures = set()
        
        # Clean and normalize names
        first_clean = re.sub(r"[^a-z]", "", first_name.lower())
        last_clean = re.sub(r"[^a-z]", "", last_name.lower())
        
        if not first_clean or not last_clean:
            return signatures
        
        # Conservative patterns that require substantial overlap
        # Only flag if they share the same first AND last name combination
        signatures.add(f"{first_clean}.{last_clean}@{domain}")
        signatures.add(f"{first_clean}{last_clean}@{domain}")
        
        # Also include full first name + first 3 chars of last name (more specific)
        if len(last_clean) >= 3:
            signatures.add(f"{first_clean}.{last_clean[:3]}@{domain}")
            signatures.add(f"{first_clean}{last_clean[:3]}@{domain}")
        
        return signatures
    
    def _can_check_name_domain(self, mapping):
        """Check if name+domain checking is possible with current mapping"""
        return (mapping.get('lead_first') != "Not Available" and
                mapping.get('lead_last') != "Not Available" and
                mapping.get('lead_domain') != "Not Available")


class InternalPhoneChecker:
    """Handle internal phone conflict detection within a single file with root domain support"""
    
    def __init__(self):
        self.stats = {
            'internal_phone_conflicts': 0,
            'internal_phone_conflict_details': []
        }
    
    def normalize_phone(self, phone_str):
        """Normalize phone number by removing all non-digits"""
        if not phone_str:
            return ""
        return re.sub(r"[^\d]", "", str(phone_str).strip())
    
    def get_company_identifier(self, row, company_col, domain_col):
        """Get company identifier (prefer ROOT DOMAIN, fallback to company)"""
        domain = ""
        company = ""
        root_domain = ""
        
        # Extract domain and root domain
        if domain_col and domain_col != "Not Available":
            domain_raw = str(row.get(domain_col, "")).strip()
            if domain_raw and domain_raw.lower() not in ['', 'none', 'null', 'n/a']:
                domain = domain_raw.lower()
                root_domain = extract_root_domain(domain)
        
        # Extract company (fallback)
        if company_col and company_col != "Not Available":
            company_raw = str(row.get(company_col, "")).strip()
            if company_raw:
                company = normalize_company(company_raw)
        
        # Return root domain (preferred), then domain, then company
        return root_domain if root_domain else (domain if domain else company.lower() if company else "")
    
    def run_internal_phone_check(self, lead_data, lead_ws, mapping, phone_conflict_col):
        """Check for phone conflicts within the lead file using ROOT DOMAIN logic"""
        
        if mapping.get('lead_phone') == "Not Available":
            return self.stats
        
        # Track phone to company mapping within the file
        phone_to_company = {}  # {phone: {'identifier': str, 'company': str, 'domain': str, 'row': int}}
        
        for idx, row in enumerate(lead_data, start=2):
            phone = self.normalize_phone(row.get(mapping.get('lead_phone'), ""))
            if not phone:
                continue
            
            # Get company identifier (prioritizing root domain)
            company_identifier = self.get_company_identifier(
                row, 
                mapping.get('lead_company', 'Not Available'),
                mapping.get('lead_domain', 'Not Available')
            )
            
            if not company_identifier:
                continue
            
            # Check if phone already seen with different company
            if phone in phone_to_company:
                existing_info = phone_to_company[phone]
                if existing_info['identifier'] != company_identifier:
                    # Internal conflict detected
                    current_company = str(row.get(mapping.get('lead_company', ''), "")).strip()
                    current_domain = str(row.get(mapping.get('lead_domain', ''), "")).strip()
                    current_root = extract_root_domain(current_domain) if current_domain else ""
                    
                    existing_root = extract_root_domain(existing_info['domain']) if existing_info['domain'] else ""
                    
                    # Create conflict message with root domain info
                    if current_root and existing_root:
                        conflict_msg = f"Phone used for {existing_info['company']} (root: {existing_root}) at row {existing_info['row']}"
                    elif existing_info['domain']:
                        conflict_msg = f"Phone used for {existing_info['company']} ({existing_info['domain']}) at row {existing_info['row']}"
                    else:
                        conflict_msg = f"Phone used for {existing_info['company']} at row {existing_info['row']}"
                    
                    # Write to conflict column
                    lead_ws.cell(idx, phone_conflict_col, conflict_msg)
                    
                    # Track statistics
                    self.stats['internal_phone_conflicts'] += 1
                    self.stats['internal_phone_conflict_details'].append({
                        'row': idx,
                        'phone': phone,
                        'current_company': current_company,
                        'current_domain': current_domain,
                        'current_root_domain': current_root,
                        'conflicting_company': existing_info['company'],
                        'conflicting_domain': existing_info['domain'],
                        'conflicting_root_domain': existing_root,
                        'conflicting_row': existing_info['row'],
                        'conflict_message': conflict_msg
                    })
            else:
                # First occurrence of this phone
                phone_to_company[phone] = {
                    'identifier': company_identifier,
                    'company': str(row.get(mapping.get('lead_company', ''), "")).strip(),
                    'domain': str(row.get(mapping.get('lead_domain', ''), "")).strip(),
                    'row': idx
                }
        
        return self.stats