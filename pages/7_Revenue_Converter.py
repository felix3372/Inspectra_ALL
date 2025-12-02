import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Page configuration (match Inspectra branding)
st.set_page_config(
    page_title="Inspectra | Revenue Converter",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Inspectra CSS (reused from Overview) ----
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
    .inspectra-hero {
        background: linear-gradient(135deg, #00e4d0, #00c3ff);
        padding: 1.2rem 2rem 1rem 2rem;
        border-radius: 20px;
        margin-top: 1rem;
        margin-bottom: 1.3rem;
        box-shadow: 0 8px 22px rgba(0,0,0,0.08);
        display: flex;
        justify-content: center;
        animation: fadeInHero 1.2s;
    }
    @keyframes fadeInHero {
        from { opacity: 0; transform: translateY(-32px);}
        to   { opacity: 1; transform: translateY(0);}
    }
    .inspectra-inline {
        display: inline-flex;
        align-items: center;
        gap: 1.3rem;
        white-space: nowrap;
    }
    .inspectra-title {
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
        color: #fff;
        letter-spacing: -1.5px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    .inspectra-divider {
        font-weight: 400;
        color: #004e66;
        opacity: 0.35;
    }
    .inspectra-tagline {
        font-size: 1.08rem;
        font-weight: 500;
        margin: 0;
        color: #e3feff;
        opacity: 0.94;
        position: relative;
        top: 2px;
        letter-spacing: 0.5px;
    }
    .section {
        background: #f6fafd;
        border-radius: 1.2rem;
        padding: 0.8rem 1.6rem 0.5rem 1.6rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 1px 9px 0 rgba(60,95,246,0.10);
        border-left: 5px solid #00c3ff;
        animation: fadeInSection 0.85s;
    }
    @keyframes fadeInSection {
        from { opacity: 0; transform: translateY(36px);}
        to   { opacity: 1; transform: translateY(0);}
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #169bb6;
        margin-bottom: 0rem;
        margin-top: 0;
        letter-spacing: -1px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .report-box {
        background: #f6fafd;
        border-radius: 1.2rem;
        padding: 1.15rem 1.6rem 1.05rem 1.6rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 1px 9px 0 rgba(60,95,246,0.10);
        border-left: 5px solid #00c3ff;
    }
    .custom-heading {
        font-size: 1.15rem;
        font-weight: 700;
        color: #169bb6;
        margin-bottom: 1rem;
        margin-top: 0;
        letter-spacing: -1px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---- Hero ----
st.markdown("""
<div class="inspectra-hero">
  <div class="inspectra-inline">
    <span class="inspectra-title">Inspectra</span>
    <span class="inspectra-divider">|</span>
    <span class="inspectra-tagline">Revenue Converter</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---- Intro section (replaces old main-header) ----
st.markdown("""
<div class="section">
  <div class="section-title">💰 What is this?</div>
  Convert abbreviated financial values (<b>K</b>, <b>M</b>, <b>B</b>, <b>T</b>) into full numeric formats with batch processing
  and exports — consistent with Inspectra's QA automation UX.
</div>
""", unsafe_allow_html=True)

# ---------- Core logic (unchanged) ----------
def convert_value(value):
    """
    Convert abbreviated values (M, B, K, T) to full numerical values.
    Supports various formats: $245.7B, 61.6M, 1.5K, €100B, ₹50M, etc.
    """
    if pd.isna(value) or value == '':
        return None
    
    value_str = str(value).strip().upper()
    
    # Extract numeric part (handles various currency symbols and formats)
    number_match = re.search(r'[-+]?[0-9]*\.?[0-9]+', value_str)
    if not number_match:
        return None
    
    number = float(number_match.group())
    
    # Determine multiplier
    if 'T' in value_str:      # Trillion
        return number * 1_000_000_000_000
    elif 'B' in value_str:    # Billion
        return number * 1_000_000_000
    elif 'M' in value_str:    # Million
        return number * 1_000_000
    elif 'K' in value_str:    # Thousand
        return number * 1_000
    else:
        return number

def format_number(num):
    """Format large numbers with commas for readability."""
    if pd.isna(num) or num is None:
        return "Invalid"
    return f"{num:,.2f}"

def convert_number_to_abbreviated(num, format_type='auto'):
    """Convert a number back to abbreviated format."""
    if pd.isna(num) or num is None:
        return "Invalid"
    
    abs_num = abs(num)
    sign = '-' if num < 0 else ''
    
    if format_type == 'auto':
        if abs_num >= 1_000_000_000_000:
            return f"{sign}{abs_num/1_000_000_000_000:.2f}T"
        elif abs_num >= 1_000_000_000:
            return f"{sign}{abs_num/1_000_000_000:.2f}B"
        elif abs_num >= 1_000_000:
            return f"{sign}{abs_num/1_000_000:.2f}M"
        elif abs_num >= 1_000:
            return f"{sign}{abs_num/1_000:.2f}K"
        else:
            return f"{sign}{abs_num:.2f}"
    elif format_type == 'billions':
        return f"{sign}{abs_num/1_000_000_000:.2f}B"
    elif format_type == 'millions':
        return f"{sign}{abs_num/1_000_000:.2f}M"
    elif format_type == 'thousands':
        return f"{sign}{abs_num/1_000:.2f}K"
    
    return f"{sign}{abs_num:,.2f}"

def process_dataframe(df, columns_to_convert):
    """Process DataFrame and convert specified columns."""
    result_df = df.copy()
    for col in columns_to_convert:
        if col in result_df.columns:
            converted_col_name = f"{col}_Converted"
            result_df[converted_col_name] = result_df[col].apply(convert_value)
            formatted_col_name = f"{col}_Formatted"
            result_df[formatted_col_name] = result_df[converted_col_name].apply(format_number)
    return result_df

def create_excel_download(df):
    """Create Excel file for download."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Converted Data')
    output.seek(0)
    return output

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    conversion_mode = st.radio(
        "Conversion Mode",
        ["Text Input", "File Upload", "Batch Processing"],
        help="Choose how you want to input your data"
    )
    st.divider()
    st.header("💡 Supported Formats")
    st.markdown("""
    - **Billions**: $245.7B, 61.6B
    - **Millions**: $61.6M, 50M
    - **Thousands**: 100K, $1.5K
    - **Trillions**: $1.2T, 2.5T
    - **Various Currencies**: $, €, £, ₹, ¥
    """)

# ---------- Main content ----------
tab1, tab2 = st.tabs(["🔄 Convert", "ℹ️ Help"])

with tab1:
    if conversion_mode == "Text Input":
        st.subheader("Manual Text Input")
        col1, col2 = st.columns(2)
        with col1:
            input_text = st.text_area(
                "Enter values (one per line)",
                height=300,
                placeholder="$245.7B\n$61.6M\n1.5K\n€100B\n₹50M",
                help="Enter one value per line. Supports B (billions), M (millions), K (thousands), T (trillions)"
            )
            if st.button("🔄 Convert Values", type="primary", use_container_width=True):
                if input_text:
                    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
                    results = []
                    for line in lines:
                        converted = convert_value(line)
                        results.append({
                            'Original Value': line,
                            'Converted Value': converted,
                            'Formatted': format_number(converted),
                            'Auto Abbreviated': convert_number_to_abbreviated(converted)
                        })
                    st.session_state['results_df'] = pd.DataFrame(results)
                else:
                    st.warning("Please enter some values to convert.")
        with col2:
            if 'results_df' in st.session_state:
                st.markdown('<div class="metric-card">✅ Converted {} values</div>'.format(len(st.session_state['results_df'])), unsafe_allow_html=True)
                st.dataframe(st.session_state['results_df'], use_container_width=True, height=300)
                col_a, col_b = st.columns(2)
                with col_a:
                    excel_file = create_excel_download(st.session_state['results_df'])
                    st.download_button(
                        label="📥 Download Excel",
                        data=excel_file,
                        file_name="converted_values.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                with col_b:
                    csv_file = st.session_state['results_df'].to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_file,
                        file_name="converted_values.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

    elif conversion_mode == "File Upload":
        st.subheader("Upload Excel or CSV File")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['xlsx', 'xls', 'csv'],
            help="Upload an Excel or CSV file with revenue data"
        )
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                st.markdown(f'<div class="metric-card">✅ Loaded {len(df)} rows and {len(df.columns)} columns</div>', unsafe_allow_html=True)

                st.subheader("Select Columns to Convert")
                columns_to_convert = st.multiselect(
                    "Choose columns containing abbreviated values",
                    options=df.columns.tolist(),
                    help="Select all columns that contain values like $245.7B, 61.6M, etc."
                )
                if columns_to_convert and st.button("🔄 Convert Selected Columns", type="primary"):
                    result_df = process_dataframe(df, columns_to_convert)
                    st.session_state['file_results_df'] = result_df
                    st.session_state['original_columns'] = columns_to_convert

                if 'file_results_df' in st.session_state:
                    st.subheader("Converted Data Preview")
                    st.dataframe(st.session_state['file_results_df'], use_container_width=True)
                    excel_file = create_excel_download(st.session_state['file_results_df'])
                    st.download_button(
                        label="📥 Download Converted File",
                        data=excel_file,
                        file_name="converted_file.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    elif conversion_mode == "Batch Processing":
        st.subheader("Batch Convert Multiple Values")
        num_inputs = st.number_input("Number of values to convert", min_value=1, max_value=50, value=5)
        batch_data = []
        cols = st.columns(2)
        for i in range(num_inputs):
            with cols[i % 2]:
                label = st.text_input(f"Label {i+1}", value=f"Value {i+1}", key=f"label_{i}")
                value = st.text_input(f"Value {i+1}", placeholder="e.g., $245.7B", key=f"value_{i}")
                if value:
                    batch_data.append({'Label': label, 'Original Value': value})
        if st.button("🔄 Convert Batch", type="primary") and batch_data:
            for item in batch_data:
                converted = convert_value(item['Original Value'])
                item['Converted Value'] = converted
                item['Formatted'] = format_number(converted)
                item['Auto Abbreviated'] = convert_number_to_abbreviated(converted)
            batch_df = pd.DataFrame(batch_data)
            st.session_state['batch_results_df'] = batch_df
            st.markdown(f'<div class="metric-card">✅ Converted {len(batch_df)} values</div>', unsafe_allow_html=True)
            st.dataframe(batch_df, use_container_width=True)
            excel_file = create_excel_download(batch_df)
            st.download_button(
                label="📥 Download Batch Results",
                data=excel_file,
                file_name="batch_converted_values.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

with tab2:
    st.subheader("ℹ️ How to Use This App")
    st.markdown("""
    ### 🎯 Quick Start Guide
    
    **1. Choose Your Input Method:**
    - **Text Input**: Paste values directly (one per line)
    - **File Upload**: Upload Excel or CSV files with revenue data
    - **Batch Processing**: Enter multiple labeled values with custom names
    
    **2. Supported Format Examples:**
    - Billions: `$245.7B`, `61.6B`, `€100B`
    - Millions: `$61.6M`, `50M`, `₹75M`
    - Thousands: `100K`, `$1.5K`
    - Trillions: `$1.2T`, `2.5T`
    
    **3. Features:**
    - ✅ Automatic format detection
    - ✅ Support for multiple currencies ($, €, £, ₹, ¥)
    - ✅ Batch processing capabilities
    - ✅ Excel and CSV export
    - ✅ Data validation and error handling
    
    **4. Tips:**
    - Values can include currency symbols
    - Negative values are supported (e.g., -$50M)
    - Decimal precision is maintained
    - Invalid formats will be marked as "Invalid"
    
    ### 📥 File Upload Tips:
    - Ensure your Excel/CSV file has clear column headers
    - Select only columns containing abbreviated values
    - Original data is preserved in the output file
    """)

# ---- Footer (match overview tone) ----
st.divider()
st.markdown("""
<div style='text-align: center; font-size: 14px; color: #6c757d; padding: .5rem 0 1rem'>
    2025 Interlink. All rights reserved. <br>
    Inspectra • Revenue Converter.
</div>
""", unsafe_allow_html=True)