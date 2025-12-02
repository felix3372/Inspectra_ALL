import pycountry

def get_all_valid_countries():
    # Only official ISO 3166 country names (no abbreviations)
    return set(country.name.lower() for country in pycountry.countries)

def find_first_invalid_country(ws):
    headers = [cell.value for cell in ws[1]]
    if "Country" not in headers:
        return "Missing 'Country' column.", None
    col_country = headers.index("Country") + 1
    valid_countries = get_all_valid_countries()
    for row in range(2, ws.max_row + 1):
        value = ws.cell(row, col_country).value
        country_name = str(value).strip().lower() if value else ""
        if country_name and country_name not in valid_countries:
            return value, row
    return None, None  # All countries valid
