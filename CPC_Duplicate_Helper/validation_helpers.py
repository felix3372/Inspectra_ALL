"""
Enhanced validation helper functions for mapping and configuration validation
Supports both single-file (internal) and dual-file (external) validation modes
"""

def validate_internal_cpc_mapping(mapping):
    """Validate CPC mapping configuration for internal validation (single file)"""
    return (mapping.get('lead_company') != "Not Available" or
            mapping.get('lead_tal') != "Not Available" or
            mapping.get('lead_domain') != "Not Available")

def validate_external_cpc_mapping(mapping):
    """Validate CPC mapping configuration for external validation (dual file)"""
    cpc_pairs = [
        (mapping.get('delivery_company'), mapping.get('lead_company')),
        (mapping.get('delivery_tal'), mapping.get('lead_tal')),
        (mapping.get('delivery_domain'), mapping.get('lead_domain'))
    ]
    return any((d != "Not Available" and l != "Not Available") for d, l in cpc_pairs)

def validate_internal_duplicate_mapping(mapping):
    """Validate duplicate check mapping configuration for internal validation (single file)"""
    email_ok = mapping.get('lead_email') != "Not Available"
    linkedin_ok = mapping.get('lead_linkedin') != "Not Available"
    name_domain_ok = all([
        mapping.get('lead_first') != "Not Available",
        mapping.get('lead_last') != "Not Available",
        mapping.get('lead_domain') != "Not Available"
    ])
    return email_ok or linkedin_ok or name_domain_ok

def validate_external_duplicate_mapping(mapping):
    """Validate duplicate check mapping configuration for external validation (dual file)"""
    email_ok = (mapping.get('delivery_email') != "Not Available" and 
                mapping.get('lead_email') != "Not Available")
    
    linkedin_ok = (mapping.get('delivery_linkedin') != "Not Available" and 
                   mapping.get('lead_linkedin') != "Not Available")
    
    name_domain_ok = all([
        mapping.get('delivery_first') != "Not Available",
        mapping.get('lead_first') != "Not Available",
        mapping.get('delivery_last') != "Not Available",
        mapping.get('lead_last') != "Not Available",
        mapping.get('delivery_domain') != "Not Available",
        mapping.get('lead_domain') != "Not Available"
    ])
    
    return email_ok or linkedin_ok or name_domain_ok

def validate_internal_phone_mapping(mapping):
    """Validate phone conflict mapping configuration for internal validation (single file)"""
    phone_ok = mapping.get('lead_phone') != "Not Available"
    company_ok = (mapping.get('lead_company') != "Not Available" or
                  mapping.get('lead_domain') != "Not Available")
    return phone_ok and company_ok

def validate_external_phone_mapping(mapping):
    """Validate phone conflict mapping configuration for external validation (dual file)"""
    phone_ok = (mapping.get('delivery_phone') != "Not Available" and 
                mapping.get('lead_phone') != "Not Available")
    
    company_ok = (mapping.get('delivery_company') != "Not Available" and 
                  mapping.get('lead_company') != "Not Available")
    
    return phone_ok and company_ok

def get_validation_errors(mapping, checks, is_first_delivery):
    """Get all validation errors for the current configuration"""
    errors = []
    
    if is_first_delivery:
        # Internal validation mode
        if checks.get('check_cpc') and not validate_internal_cpc_mapping(mapping):
            errors.append("CPC check enabled — map at least one of Company, TAL Company, or Domain in the lead file.")
        
        if checks.get('check_duplicates') and not validate_internal_duplicate_mapping(mapping):
            errors.append("Duplicate check enabled — map Email OR LinkedIn OR (First + Last + Domain) in the lead file.")
        
        if checks.get('check_phone') and not validate_internal_phone_mapping(mapping):
            errors.append("Phone conflict check enabled — map Phone Number AND (Company Name OR Domain) in the lead file.")
    else:
        # External validation mode (original logic)
        if checks.get('check_cpc') and not validate_external_cpc_mapping(mapping):
            errors.append("CPC check enabled — map at least one of Company, TAL Company, or Domain in BOTH files.")
        
        if checks.get('check_duplicates') and not validate_external_duplicate_mapping(mapping):
            errors.append("Duplicate check enabled — map Email OR LinkedIn OR (First + Last + Domain) in BOTH files.")
        
        if checks.get('check_phone') and not validate_external_phone_mapping(mapping):
            errors.append("Phone conflict check enabled — map Phone Number AND Company Name in BOTH files.")
    
    return errors

# Backward compatibility functions (keep original names for existing code)
def validate_cpc_mapping(mapping):
    """Validate CPC mapping configuration (backward compatibility)"""
    return validate_external_cpc_mapping(mapping)

def validate_duplicate_mapping(mapping):
    """Validate duplicate check mapping configuration (backward compatibility)"""
    return validate_external_duplicate_mapping(mapping)

def validate_phone_mapping(mapping):
    """Validate phone conflict mapping configuration (backward compatibility)"""
    return validate_external_phone_mapping(mapping)