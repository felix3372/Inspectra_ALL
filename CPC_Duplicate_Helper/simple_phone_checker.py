import re
from utils.email_utils import extract_root_domain

class SimplePhoneChecker:
    """Simple phone checker - just check if phone was used for different company in delivery"""
    
    def __init__(self):
        self.delivery_phone_to_domain = {}  # {phone: domain}
        self.stats = {
            'phone_conflicts': 0,
            'phone_conflict_details': []
        }
    
    def normalize_phone(self, phone_str):
        """Normalize phone number by removing all non-digits"""
        if not phone_str:
            return ""
        return re.sub(r"[^\d]", "", str(phone_str).strip())
    
    def get_domain_identifier(self, row, company_col, domain_col):
        """Get domain identifier (prefer domain, fallback to company)"""
        domain = ""
        company = ""
        
        # Extract domain
        if domain_col and domain_col != "Not Available":
            domain_raw = str(row.get(domain_col, "")).strip()
            if domain_raw and domain_raw.lower() not in ['', 'none', 'null', 'n/a']:
                domain = extract_root_domain(domain_raw.lower()) or domain_raw.lower()
        
        # Extract company (fallback)
        if not domain and company_col and company_col != "Not Available":
            company_raw = str(row.get(company_col, "")).strip()
            if company_raw:
                company = company_raw.strip()
        
        # Return domain (preferred) or company (fallback)
        return domain if domain else company.lower() if company else ""
    
    def build_delivery_phone_map(self, delivery_data, phone_col, company_col, domain_col):
        """Build simple mapping: phone -> domain/company from delivery file"""
        if phone_col == "Not Available":
            return
            
        for row in delivery_data:
            phone = self.normalize_phone(row.get(phone_col, ""))
            if not phone:
                continue
                
            identifier = self.get_domain_identifier(row, company_col, domain_col)
            if identifier:
                # Store first occurrence only
                if phone not in self.delivery_phone_to_domain:
                    self.delivery_phone_to_domain[phone] = {
                        'identifier': identifier,
                        'company': str(row.get(company_col, "")).strip() if company_col != "Not Available" else "",
                        'domain': str(row.get(domain_col, "")).strip() if domain_col != "Not Available" else ""
                    }
    
    def check_phone_conflicts(self, lead_data, lead_ws, phone_col, company_col, domain_col, conflict_col):
        """Check if phone from lead was used for different company in delivery"""
        if phone_col == "Not Available":
            return
        
        for idx, row in enumerate(lead_data, start=2):
            phone = self.normalize_phone(row.get(phone_col, ""))
            if not phone:
                continue
                
            # Get lead identifier
            lead_identifier = self.get_domain_identifier(row, company_col, domain_col)
            if not lead_identifier:
                continue
            
            # Check if phone was used in delivery for different company
            if phone in self.delivery_phone_to_domain:
                delivery_info = self.delivery_phone_to_domain[phone]
                delivery_identifier = delivery_info['identifier']
                
                # Different company/domain = conflict
                if delivery_identifier != lead_identifier:
                    # Get display names
                    lead_company = str(row.get(company_col, "")).strip() if company_col != "Not Available" else ""
                    lead_domain = str(row.get(domain_col, "")).strip() if domain_col != "Not Available" else ""
                    
                    delivery_company = delivery_info['company']
                    delivery_domain = delivery_info['domain']
                    
                    # Create conflict message
                    if delivery_domain and lead_domain:
                        conflict_msg = f"Phone used for {delivery_company} ({delivery_domain}) in delivery file"
                    elif delivery_domain:
                        conflict_msg = f"Phone used for {delivery_company} ({delivery_domain}) in delivery file"
                    elif lead_domain:
                        conflict_msg = f"Phone used for {delivery_company} in delivery file"
                    else:
                        conflict_msg = f"Phone used for {delivery_company} in delivery file"
                    
                    # Write to conflict column
                    lead_ws.cell(idx, conflict_col, conflict_msg)
                    
                    # Track statistics
                    self.stats['phone_conflicts'] += 1
                    self.stats['phone_conflict_details'].append({
                        'row': idx,
                        'phone': phone,
                        'lead_company': lead_company,
                        'lead_domain': lead_domain,
                        'delivery_company': delivery_company,
                        'delivery_domain': delivery_domain,
                        'conflict_message': conflict_msg
                    })
    
    def get_stats(self):
        """Return simple statistics"""
        return {
            'phone_conflicts': self.stats['phone_conflicts'],
            'phone_conflict_details': self.stats['phone_conflict_details']
        }