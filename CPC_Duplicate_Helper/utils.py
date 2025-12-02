def normalize_company(name):
    """Normalize company names for better matching"""
    if not name:
        return ""
    
    # Common company suffixes to remove
    suffixes = [
        ', inc.', ' inc.', ', inc', ' inc',
        ', llc', ' llc', ', l.l.c.', ' l.l.c.',
        ', ltd.', ' ltd.', ', ltd', ' ltd',
        ', limited', ' limited',
        ', corp.', ' corp.', ', corp', ' corp',
        ', corporation', ' corporation',
        ', co.', ' co.', ', co', ' co',
        ', company', ' company',
        ', gmbh', ' gmbh',
        ', s.a.', ' s.a.', ', sa', ' sa',
        ', plc', ' plc', ', p.l.c.', ' p.l.c.',
        ', llp', ' llp', ', l.l.p.', ' l.l.p.',
        ', lp', ' lp', ', l.p.', ' l.p.',
        ', ag', ' ag', ', a.g.', ' a.g.',
        ', nv', ' nv', ', n.v.', ' n.v.',
        ', bv', ' bv', ', b.v.', ' b.v.'
    ]
    
    normalized = name.strip().lower()
    
    # Remove common prefixes
    prefixes = ['the ', 'a ']
    for prefix in prefixes:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    
    # Remove suffixes
    for suffix in suffixes:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
            break
    
    # Remove special characters but keep alphanumeric
    normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
    normalized = ' '.join(normalized.split())  # Normalize whitespace
    
    return normalized

def ensure_col_in_ws(ws_headers, ws, name):
    """Ensure a column exists in worksheet and return its position"""
    if name in ws_headers:
        return ws_headers.index(name) + 1
    else:
        ws_headers.append(name)
        col_idx = len(ws_headers)
        ws.cell(1, col_idx, name)
        return col_idx

def get_smart_suggestions(headers, keywords):
    """Get smart column suggestions based on keywords"""
    return [h for h in headers if any(
        keyword in h.lower() for keyword in keywords
    )]