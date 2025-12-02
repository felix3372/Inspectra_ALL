import phonenumbers
import pycountry
from phonenumbers import geocoder
from .country_code_prefix_validator import is_valid_us_ca_number


def validate_phone_by_country(wb, ws):
    # Extract header indices
    header_row = [str(cell.value).strip().lower() for cell in ws[1]]
    try:
        col_country = header_row.index("country") + 1
        col_phone = header_row.index("phone number") + 1
    except ValueError:
        raise ValueError("Country and/or Phone Number column not found.")

    # Add 'Phone Validation' header if not present
    col_validation = len(header_row) + 1
    if len(ws[1]) < col_validation or (ws.cell(1, col_validation).value or "").strip().lower() != "phone validation":
        ws.cell(1, col_validation).value = "Phone Validation"

    us_names = {"united states", "united states of america", "usa", "us", "america"}
    ca_names = {"canada", "ca"}

    for row in range(2, ws.max_row + 1):
        country = ws.cell(row, col_country).value
        phone = str(ws.cell(row, col_phone).value or "").strip()
        country_str = str(country or "").strip()
        validation = "Invalid"

        if country_str and phone:
            country_lower = country_str.lower()
            digits = ''.join(filter(str.isdigit, phone))
            region = ""

            if country_lower in us_names or country_lower in ca_names:
                # North America forgiving validation
                if len(digits) == 10:
                    digits = "1" + digits
                if is_valid_us_ca_number(digits):
                    try:
                        parsed = phonenumbers.parse("+" + digits, "US" if country_lower in us_names else "CA")
                        region = geocoder.description_for_number(parsed, "en")
                        validation = f"{country_str}, Valid"
                        if region:
                            validation += f", {region}"
                    except Exception:
                        validation = f"{country_str}, Valid"
                else:
                    validation = f"{country_str}, Invalid"
            else:
                # All other countries: strict phonenumbers validation
                try:
                    country_obj = pycountry.countries.get(name=country_str)
                    country_iso = country_obj.alpha_2 if country_obj else None
                    parsed = phonenumbers.parse("+" + digits, country_iso)
                    is_valid = phonenumbers.is_valid_number(parsed)
                    if is_valid:
                        region = geocoder.description_for_number(parsed, "en")
                        validation = f"{country_str}, Valid"
                        if region:
                            validation += f", {region}"
                    else:
                        validation = f"{country_str}, Invalid"
                except Exception:
                    validation = f"{country_str}, Invalid"
        else:
            validation = f"{country_str}, Invalid"

        ws.cell(row, col_validation).value = validation

    return wb, ws
