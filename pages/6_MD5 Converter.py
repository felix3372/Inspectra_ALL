import streamlit as st
import hashlib
import pandas as pd
from io import BytesIO
import time

# Page configuration
st.set_page_config(
    page_title="Inspectra | MD5 Hash Generator",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Inspectra CSS ----
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
    <span class="inspectra-tagline">MD5 Hash Generator</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---- Intro section ----
st.markdown("""
<div class="section">
  <div class="section-title">🔒 What is this?</div>
  Generate MD5 hashes in bulk with batch processing and export capabilities — consistent with Inspectra's QA automation UX.
</div>
""", unsafe_allow_html=True)

# ---------- Core Functions ----------
def generate_md5_hash(text):
    """Generate MD5 hash for given text"""
    return hashlib.md5(text.encode()).hexdigest()

def create_excel_download(df):
    """Create Excel file for download"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='MD5 Hashes')
    output.seek(0)
    return output

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    include_original = st.checkbox("Include original text in output", value=True)
    use_uppercase = st.checkbox("Uppercase Hash Output", value=False)
    show_timestamp = st.checkbox("Show Timestamp", value=False)
    
    st.divider()
    st.header("💡 About MD5")
    st.markdown("""
    **MD5 (Message Digest Algorithm 5):**
    - 128-bit hash value
    - Produces 32-character hexadecimal output
    - Commonly used for checksums and data integrity
    - **Note**: Not recommended for cryptographic security
    
    **Use Cases:**
    - File integrity verification
    - Quick data checksums
    - Non-security hash generation
    - Testing and development
    """)

# ---------- Main Content ----------
tab1, tab2 = st.tabs(["🔄 Generate Hashes", "ℹ️ Help"])

with tab1:
    st.subheader("Batch MD5 Hash Generation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        batch_input = st.text_area(
            "Enter multiple lines of text (one per line):",
            height=300,
            placeholder="Example:\npassword\nadmin\nhello123\ntest@email.com",
            help="Enter one value per line to generate MD5 hashes"
        )
        
        if st.button("🔄 Generate MD5 Hashes", type="primary", use_container_width=True):
            if batch_input.strip():
                lines = [line.strip() for line in batch_input.split('\n') if line.strip()]
                results = []

                for idx, line in enumerate(lines, start=1):
                    start_time = time.time()
                    hash_value = generate_md5_hash(line)
                    end_time = time.time()

                    if use_uppercase:
                        hash_value = hash_value.upper()

                    result = {
                        'Index': idx,
                        'MD5 Hash': hash_value,
                    }

                    if include_original:
                        result['Original Text'] = line

                    if show_timestamp:
                        result['Generated Time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        result['Time Taken (ms)'] = round((end_time - start_time) * 1000, 3)

                    results.append(result)

                df = pd.DataFrame(results)
                st.session_state['batch_results'] = df
            else:
                st.warning("⚠️ Please enter some text to process.")
    
    with col2:
        if 'batch_results' in st.session_state:
            st.markdown('<div class="metric-card">✅ Generated {} MD5 hashes successfully!</div>'.format(
                len(st.session_state['batch_results'])
            ), unsafe_allow_html=True)
            
            st.dataframe(st.session_state['batch_results'], use_container_width=True, height=300)
            
            # Export buttons
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                csv_data = st.session_state['batch_results'].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="md5_hashes.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_b:
                excel_data = create_excel_download(st.session_state['batch_results'])
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="md5_hashes.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col_c:
                json_data = st.session_state['batch_results'].to_json(orient='records', indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name="md5_hashes.json",
                    mime="application/json",
                    use_container_width=True
                )

with tab2:
    st.subheader("ℹ️ How to Use This App")
    st.markdown("""
    ### 🎯 Quick Start Guide
    
    **1. Enter Your Data:**
    - Paste text values in the input area (one per line)
    - Can include passwords, emails, usernames, or any text
    
    **2. Configure Settings (Sidebar):**
    - **Include Original Text**: Show input alongside hash
    - **Uppercase Output**: Convert hash to uppercase
    - **Show Timestamp**: Add generation time info
    
    **3. Generate & Export:**
    - Click "Generate MD5 Hashes" button
    - View results in the table
    - Download as CSV, Excel, or JSON
    
    ### 🔒 Security Notice
    
    **Important**: MD5 is **not** cryptographically secure for:
    - Password storage (use bcrypt, Argon2, or PBKDF2)
    - Digital signatures
    - Security-critical applications
    
    **Good for**:
    - File integrity checks
    - Quick checksums
    - Non-security hashing
    - Testing and development
    
    ### 📋 Example Use Cases
    
    1. **Testing**: Generate test data hashes
    2. **Data Comparison**: Create checksums for file verification
    3. **Development**: Quick hash generation for prototypes
    4. **Documentation**: Generate example hashes for documentation
    
    ### 💡 Tips
    
    - Empty lines are automatically skipped
    - Leading/trailing whitespace is trimmed
    - Each line generates one unique hash
    - Export formats preserve all selected options
    """)

# ---- Footer ----
st.divider()
st.markdown("""
<div style='text-align: center; font-size: 14px; color: #6c757d; padding: .5rem 0 1rem'>
    2025 Interlink. All rights reserved. <br>
    Inspectra • MD5 Hash Generator.
</div>
""", unsafe_allow_html=True)