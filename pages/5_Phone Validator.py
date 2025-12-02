import streamlit as st
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import pandas as pd

st.set_page_config(page_title="Phone Number Validator", page_icon="📱", layout="wide")

st.title("📱 Phone Number Validator")
st.markdown("Validate and get detailed information about phone numbers from around the world.")

def checkphone(phone_input, display=True):
    """Validate and extract information from a phone number"""
    # Auto-add "+" if missing and input looks like an international number
    if not phone_input.startswith("+"):
        phone_input = "+" + phone_input.strip()
    
    try:
        # Parse the phone number
        parsed_number = phonenumbers.parse(phone_input, None)
        
        # Validate the phone number
        is_valid = phonenumbers.is_valid_number(parsed_number)
        
        # Get detailed information
        country = geocoder.description_for_number(parsed_number, "en")
        sim_carrier = carrier.name_for_number(parsed_number, "en")
        country_code = parsed_number.country_code
        national_number = parsed_number.national_number
        
        # Get timezone
        timezones = timezone.time_zones_for_number(parsed_number)
        tz_str = ", ".join(timezones) if timezones else "Unknown"
        
        # Format in different styles
        international_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        national_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        e164_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        
        # Only display results if requested (for single number validation)
        if display:
            # Validation status
            if is_valid:
                st.success("✅ Valid phone number")
            else:
                st.error("❌ Invalid phone number")
            
            # Compact info display
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Country:** {country if country else 'Unknown'}")
                st.write(f"**Country Code:** +{country_code}")
            
            with col2:
                st.write(f"**Carrier:** {sim_carrier if sim_carrier else 'Unknown'}")
                st.write(f"**Timezone:** {tz_str}")
            
            with col3:
                st.write(f"**International:** {international_format}")
                st.write(f"**E.164:** {e164_format}")
        
        # Return data for batch processing
        return {
            "original": phone_input,
            "is_valid": is_valid,
            "country": country if country else "Unknown",
            "carrier": sim_carrier if sim_carrier else "Unknown",
            "international": international_format,
            "e164": e164_format,
            "timezone": tz_str
        }

    except phonenumbers.NumberParseException as e:
        if display:
            st.error(f"❌ Error parsing number: {e}")
        return {
            "original": phone_input,
            "is_valid": False,
            "country": "Error",
            "carrier": "Error",
            "international": "Error",
            "e164": "Error",
            "timezone": "Error",
            "error": str(e)
        }

# Main input section
st.header("Single Number Validation")

col1, col2 = st.columns([3, 1])

with col1:
    phone_input = st.text_input(
        "Enter a phone number (with country code):",
        value="61872252566",
        help="Enter the number with country code. The '+' sign is optional.",
        placeholder="e.g., +1234567890 or 1234567890"
    )

with col2:
    st.write("")  # Spacing
    st.write("")  # Spacing
    validate_button = st.button("🔍 Validate", type="primary", use_container_width=True)

if phone_input and (validate_button or True):  # Auto-validate on input
    st.markdown("---")
    checkphone(phone_input)

# Batch processing section
st.markdown("---")
st.header("Batch Processing")

tab1, tab2 = st.tabs(["📁 Upload File", "📝 Paste Numbers"])

with tab1:
    st.markdown("Upload a CSV or Excel file with phone numbers")
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'], label_visibility="collapsed")
    
    if uploaded_file:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        column_name = st.selectbox("Select the column with phone numbers:", df.columns)
        
        if st.button("🚀 Process File", type="primary"):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, phone in enumerate(df[column_name]):
                status_text.text(f"Processing {idx + 1}/{len(df)}...")
                result = checkphone(str(phone), display=False)  # No display during batch
                results.append(result)
                progress_bar.progress((idx + 1) / len(df))
            
            status_text.success(f"✅ Processed {len(results)} numbers!")
            progress_bar.empty()
            
            # Display results
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
            
            # Summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Numbers", len(results_df))
            with col2:
                st.metric("Valid", results_df['is_valid'].sum())
            with col3:
                st.metric("Invalid", (~results_df['is_valid']).sum())
            
            # Download button
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="phone_validation_results.csv",
                mime="text/csv"
            )

with tab2:
    st.markdown("Enter phone numbers (one per line)")
    bulk_input = st.text_area(
        "Phone numbers:",
        height=200,
        placeholder="61872252566\n+1234567890\n+447123456789",
        label_visibility="collapsed"
    )
    
    if st.button("🚀 Process Numbers", type="primary"):
        if bulk_input.strip():
            phone_numbers = [line.strip() for line in bulk_input.split('\n') if line.strip()]
            
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, phone in enumerate(phone_numbers):
                status_text.text(f"Processing {idx + 1}/{len(phone_numbers)}...")
                result = checkphone(phone, display=False)  # No display during batch
                results.append(result)
                progress_bar.progress((idx + 1) / len(phone_numbers))
            
            status_text.success(f"✅ Processed {len(results)} numbers!")
            progress_bar.empty()
            
            # Display results
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
            
            # Summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Numbers", len(results_df))
            with col2:
                st.metric("Valid", results_df['is_valid'].sum())
            with col3:
                st.metric("Invalid", (~results_df['is_valid']).sum())
            
            # Download button
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="phone_validation_results.csv",
                mime="text/csv"
            )
        else:
            st.warning("Please enter at least one phone number")

# Footer with info
st.markdown("---")
st.markdown("""
**Tips:**
- Country codes are required (e.g., +1 for USA, +44 for UK, +61 for Australia)
- The '+' sign is optional - it will be added automatically
- Batch process multiple numbers by uploading a CSV or Excel file
""")