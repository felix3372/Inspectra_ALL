import streamlit as st
from .utils import get_smart_suggestions

class UIComponents:
    """Reusable UI components for the application"""
    
    @staticmethod
    def render_hero_section():
        """Render the hero section with styling"""
        st.markdown("""
        <style>
        .inspectra-hero {
            background: linear-gradient(135deg, #00e4d0, #00c3ff);
            padding: 1.2rem 2rem 1rem 2rem; border-radius: 20px;
            margin-top: 1rem; margin-bottom: 1.3rem;
            box-shadow: 0 8px 22px rgba(0,0,0,0.08);
            display: flex; justify-content: center; animation: fadeInHero 1.2s;
        }
        @keyframes fadeInHero { from { opacity: 0; transform: translateY(-32px);} to { opacity: 1; transform: translateY(0);} }
        .inspectra-inline { display: inline-flex; align-items: center; gap: 1.3rem; white-space: nowrap; }
        .inspectra-title { font-size: 2.5rem; font-weight: 900; margin: 0; color: #fff; letter-spacing: -1.5px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.08); }
        .inspectra-divider { font-weight: 400; color: #004e66; opacity: 0.35; }
        .inspectra-tagline { font-size: 1.08rem; font-weight: 500; margin: 0; color: #e3feff; opacity: 0.94; position: relative; top: 2px; letter-spacing: 0.5px; }
        .section { background: #f6fafd; border-radius: 1.2rem; padding: 1.15rem 1.6rem 1.05rem 1.6rem;
            margin-bottom: 1.1rem; box-shadow: 0 1px 9px 0 rgba(60,95,246,0.10); border-left: 5px solid #00c3ff; animation: fadeInSection 0.85s; }
        @keyframes fadeInSection { from { opacity: 0; transform: translateY(36px);} to { opacity: 1; transform: translateY(0);} }
        .section-title { font-size: 1.15rem; font-weight: 700; color: #169bb6; margin-bottom: 0rem; margin-top: 0; letter-spacing: -1px; display: flex; align-items: center; gap: 8px; }
        .custom-heading { font-size: 1.3rem; font-weight: 700; color: #169bb6; margin-bottom: 1rem; padding: 0.5rem 0; border-bottom: 2px solid #00c3ff; }
        .small-muted { font-size: 0.95rem; color: #346b79; opacity: 0.9; }
        .preview-table { font-size: 0.85rem; margin-top: 0.5rem; }
        </style>
        <div class="inspectra-hero">
            <div class="inspectra-inline">
                <span class="inspectra-title">Inspectra</span>
                <span class="inspectra-divider">|</span>
                <span class="inspectra-tagline">CPC & Duplicate Checker</span>
            </div>
        </div>
        <div class="section">
            <div class="section-title">🤖 What is this?</div>
            <b>Inspectra's CPC & Duplicate Checker</b> is a tool to automate, standardize, and visualize campaign data QA.
            Choose your delivery mode, map your fields and run CPC / duplicate / phone conflict checks to find
            disqualifications and generate an updated checked file.
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_delivery_type_selection():
        """Render delivery type selection section"""
        st.markdown("### 🎯 Step 1: Select Delivery Type")
        
        delivery_type = st.radio(
            "Is this your first delivery to this client?",
            options=["Yes - First Delivery (Internal validation only)", 
                    "No - Subsequent Delivery (Full validation)"],
            key="delivery_type",
            help="First delivery runs internal checks within your lead file. Subsequent delivery checks against previously delivered files."
        )
        
        is_first_delivery = delivery_type.startswith("Yes")
        
        if is_first_delivery:
            st.info("🔍 **Internal Validation Mode**: Only your lead file will be analyzed for internal conflicts, CPC violations, and duplicates.")
        else:
            st.info("🔄 **Full Validation Mode**: Your lead file will be checked against the previously delivered file plus internal validation.")
            
        return is_first_delivery

    @staticmethod
    def render_file_upload_section(session_state, is_first_delivery):
        """Render file upload section based on delivery type"""
        
        if is_first_delivery:
            # Single file upload for first delivery
            st.markdown("### 📄 Step 2: Upload Lead File")
            
            lead_file = st.file_uploader(
                "Upload Lead File (To Be Validated)",
                type=['xlsx', 'xlsm'],
                key="lead_upload_single",
                help="This is the file you want to validate for internal conflicts"
            )
            
            lead_info = None
            if lead_file:
                session_state.lead_file = lead_file
                lead_info = UIComponents._render_file_preview(lead_file, "lead", "preview_lead_single")
            
            return None, lead_info
        
        else:
            # Dual file upload for subsequent deliveries
            col1, col2 = st.columns(2)
            
            delivery_info = None
            lead_info = None
            
            with col1:
                st.markdown("### 📁 Step 2a: Upload Delivery File")
                delivery_file = st.file_uploader(
                    "Upload Delivery File (Already Sent)",
                    type=['xlsx', 'xlsm'],
                    key="delivery_upload",
                    help="This is the file that was already delivered to the client"
                )
                
                if delivery_file:
                    session_state.delivery_file = delivery_file
                    delivery_info = UIComponents._render_file_preview(delivery_file, "delivery", "preview_delivery")

            with col2:
                st.markdown("### 📄 Step 2b: Upload Lead File")
                lead_file = st.file_uploader(
                    "Upload New Lead File (To Be Checked)",
                    type=['xlsx', 'xlsm'],
                    key="lead_upload",
                    help="This is the new file you want to validate"
                )
                
                if lead_file:
                    session_state.lead_file = lead_file
                    lead_info = UIComponents._render_file_preview(lead_file, "lead", "preview_lead")
            
            return delivery_info, lead_info

    @staticmethod
    def _render_file_preview(file, file_type, preview_key):
        """Helper to render file preview"""
        from .file_handler import FileHandler
        
        headers, rows, cols = FileHandler.get_headers_from_upload(file)
        if headers:
            st.success(f"✅ Loaded: {file.name}")
            st.caption(f"📊 {rows:,} rows × {cols} columns")
            
            # Large file warning for lead files
            if file_type == "lead" and rows > 5000:
                st.warning(f"⚠️ Large file detected ({rows:,} rows). Processing may take a few moments.")
            
            # Preview option
            if st.checkbox(f"Preview {file_type} file", key=preview_key):
                preview_df = FileHandler.get_preview_data(file)
                if not preview_df.empty:
                    st.dataframe(preview_df, use_container_width=True, height=150)
            
            return headers, rows, cols
        
        return None, 0, 0

    @staticmethod
    def render_checks_selection():
        """Render the checks selection section"""
        st.markdown("### ⚙️ Step 3: Select Checks to Perform")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            check_cpc = st.checkbox("**Check CPC (Contact Per Company)**", value=False, key="check_cpc")
            cpc_limit = None
            if check_cpc:
                cpc_limit = st.number_input(
                    "Enter CPC Limit",
                    min_value=1,
                    max_value=1000,
                    value=st.session_state.get('cpc_limit', 3),
                    help="Maximum contacts allowed per company"
                )
        
        with col2:
            check_duplicates = st.checkbox("**Check Duplicates**", value=False, key="check_duplicates")
            if check_duplicates:
                st.caption("Will check for duplicates using email, LinkedIn, and email permutations")
        
        with col3:
            check_phone = st.checkbox("**Check Phone Conflicts**", value=False, key="check_phone")
            if check_phone:
                st.caption("Will check for phone numbers used across different companies")
        
        return check_cpc, check_duplicates, check_phone, cpc_limit

    @staticmethod
    def render_column_mapping(delivery_headers, lead_headers, check_cpc, check_duplicates, check_phone, is_first_delivery):
        """Render column mapping section based on delivery type"""
        
        if is_first_delivery:
            return UIComponents._render_single_file_mapping(lead_headers, check_cpc, check_duplicates, check_phone)
        else:
            return UIComponents._render_dual_file_mapping(delivery_headers, lead_headers, check_cpc, check_duplicates, check_phone)

    @staticmethod
    def _render_single_file_mapping(lead_headers, check_cpc, check_duplicates, check_phone):
        """Render column mapping for single file (first delivery) mode"""
        st.markdown("### 🔗 Step 4: Map Columns (Lead File)")
        
        mapping = {}
        
        # Smart suggestions
        company_suggestions = get_smart_suggestions(lead_headers, ['company', 'organization', 'org', 'employer', 'account'])
        domain_suggestions = get_smart_suggestions(lead_headers, ['domain', 'website', 'url', 'web'])
        email_suggestions = get_smart_suggestions(lead_headers, ['email'])
        linkedin_suggestions = get_smart_suggestions(lead_headers, ['linkedin'])
        first_suggestions = get_smart_suggestions(lead_headers, ['first'])
        last_suggestions = get_smart_suggestions(lead_headers, ['last'])
        phone_suggestions = get_smart_suggestions(lead_headers, ['phone', 'number', 'tel', 'mobile'])

        # CPC Mapping (single file)
        if check_cpc:
            st.markdown("#### CPC Column Mapping")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.markdown("**Company Name**")
                mapping['lead_company'] = st.selectbox(
                    "Select Company Column", ["Not Available"] + lead_headers,
                    index=1 if company_suggestions and company_suggestions[0] in lead_headers else 0,
                    key="lead_company_single"
                )
            
            with c2:
                st.markdown("**Domain**")
                mapping['lead_domain'] = st.selectbox(
                    "Select Domain Column", ["Not Available"] + lead_headers,
                    index=1 if domain_suggestions and domain_suggestions[0] in lead_headers else 0,
                    key="lead_domain_single"
                )
            
            with c3:
                st.markdown("**TAL Company Name (Optional)**")
                mapping['lead_tal'] = st.selectbox(
                    "Select TAL Company Column", ["Not Available"] + lead_headers, 
                    key="lead_tal_single"
                )

        # Duplicate Mapping (single file)
        if check_duplicates:
            st.markdown("#### Duplicate Check Column Mapping")
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                st.markdown("**Email Address**")
                mapping['lead_email'] = st.selectbox(
                    "Select Email Column", ["Not Available"] + lead_headers,
                    index=1 if email_suggestions and email_suggestions[0] in lead_headers else 0,
                    key="lead_email_single"
                )
            
            with c2:
                st.markdown("**LinkedIn Link**")
                mapping['lead_linkedin'] = st.selectbox(
                    "Select LinkedIn Column", ["Not Available"] + lead_headers,
                    index=1 if linkedin_suggestions and linkedin_suggestions[0] in lead_headers else 0,
                    key="lead_linkedin_single"
                )
            
            with c3:
                st.markdown("**First Name**")
                mapping['lead_first'] = st.selectbox(
                    "Select First Name Column", ["Not Available"] + lead_headers,
                    index=1 if first_suggestions and first_suggestions[0] in lead_headers else 0,
                    key="lead_first_single"
                )
            
            with c4:
                st.markdown("**Last Name**")
                mapping['lead_last'] = st.selectbox(
                    "Select Last Name Column", ["Not Available"] + lead_headers,
                    index=1 if last_suggestions and last_suggestions[0] in lead_headers else 0,
                    key="lead_last_single"
                )

            # Domain for permutations (only if CPC not enabled)
            if not check_cpc:
                st.markdown("**Domain (for email permutations)**")
                mapping['lead_domain'] = st.selectbox(
                    "Select Domain Column", ["Not Available"] + lead_headers,
                    index=1 if domain_suggestions and domain_suggestions[0] in lead_headers else 0,
                    key="lead_domain_dup_single"
                )

        # Phone Mapping (single file)
        if check_phone:
            st.markdown("#### Phone Conflict Column Mapping")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Phone Number**")
                mapping['lead_phone'] = st.selectbox(
                    "Select Phone Column", ["Not Available"] + lead_headers,
                    index=1 if phone_suggestions and phone_suggestions[0] in lead_headers else 0,
                    key="lead_phone_single"
                )
            
            with c2:
                # If CPC is not enabled, we need company and domain mapping for phone conflicts
                if not check_cpc:
                    st.markdown("**Company Name (for phone conflicts)**")
                    mapping['lead_company'] = st.selectbox(
                        "Select Company Column", ["Not Available"] + lead_headers,
                        index=1 if company_suggestions and company_suggestions[0] in lead_headers else 0,
                        key="lead_company_phone_single"
                    )
            
            # Domain mapping if not already set
            if not check_cpc and 'lead_domain' not in mapping:
                st.markdown("**Domain (for phone conflicts)**")
                mapping['lead_domain'] = st.selectbox(
                    "Select Domain Column", ["Not Available"] + lead_headers,
                    index=1 if domain_suggestions and domain_suggestions[0] in lead_headers else 0,
                    key="lead_domain_phone_single"
                )

        return mapping

    @staticmethod 
    def _render_dual_file_mapping(delivery_headers, lead_headers, check_cpc, check_duplicates, check_phone):
        """Render column mapping for dual file (subsequent delivery) mode"""
        st.markdown("### 🔗 Step 4: Map Columns")
        
        # Initialize mapping variables
        mapping = {}
        
        # Smart suggestions
        company_suggestions = get_smart_suggestions(delivery_headers, ['company', 'organization', 'org', 'employer', 'account'])
        domain_suggestions = get_smart_suggestions(delivery_headers, ['domain', 'website', 'url', 'web'])
        email_suggestions = get_smart_suggestions(delivery_headers, ['email'])
        linkedin_suggestions = get_smart_suggestions(delivery_headers, ['linkedin'])
        first_suggestions = get_smart_suggestions(delivery_headers, ['first'])
        last_suggestions = get_smart_suggestions(delivery_headers, ['last'])
        phone_suggestions = get_smart_suggestions(delivery_headers, ['phone', 'number', 'tel', 'mobile'])

        # CPC Mapping
        if check_cpc:
            st.markdown("#### CPC Column Mapping")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.markdown("**Map Company Name**")
                mapping['delivery_company'] = st.selectbox(
                    "From Delivery File", ["Not Available"] + delivery_headers,
                    index=1 if company_suggestions and company_suggestions[0] in delivery_headers else 0,
                    key="del_company"
                )
                mapping['lead_company'] = st.selectbox(
                    "From Lead File", ["Not Available"] + lead_headers,
                    index=1 if company_suggestions and company_suggestions[0] in lead_headers else 0,
                    key="lead_company"
                )
            
            with c2:
                st.markdown("**Map Domain**")
                mapping['delivery_domain'] = st.selectbox(
                    "From Delivery File", ["Not Available"] + delivery_headers,
                    index=1 if domain_suggestions and domain_suggestions[0] in delivery_headers else 0,
                    key="del_domain"
                )
                mapping['lead_domain'] = st.selectbox(
                    "From Lead File", ["Not Available"] + lead_headers,
                    index=1 if domain_suggestions and domain_suggestions[0] in lead_headers else 0,
                    key="lead_domain"
                )
            
            with c3:
                st.markdown("**Map TAL Company Name (Optional)**")
                mapping['delivery_tal'] = st.selectbox("From Delivery File", ["Not Available"] + delivery_headers, key="del_tal")
                mapping['lead_tal'] = st.selectbox("From Lead File", ["Not Available"] + lead_headers, key="lead_tal")

        # Duplicate Mapping
        if check_duplicates:
            st.markdown("#### Duplicate Check Column Mapping")
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                st.markdown("**Email Address**")
                mapping['delivery_email'] = st.selectbox(
                    "From Delivery File", ["Not Available"] + delivery_headers,
                    index=1 if email_suggestions and email_suggestions[0] in delivery_headers else 0,
                    key="del_email"
                )
                mapping['lead_email'] = st.selectbox(
                    "From Lead File", ["Not Available"] + lead_headers,
                    index=1 if email_suggestions and email_suggestions[0] in lead_headers else 0,
                    key="lead_email"
                )
            
            with c2:
                st.markdown("**LinkedIn Link**")
                mapping['delivery_linkedin'] = st.selectbox(
                    "From Delivery File", ["Not Available"] + delivery_headers,
                    index=1 if linkedin_suggestions and linkedin_suggestions[0] in delivery_headers else 0,
                    key="del_linkedin"
                )
                mapping['lead_linkedin'] = st.selectbox(
                    "From Lead File", ["Not Available"] + lead_headers,
                    index=1 if linkedin_suggestions and linkedin_suggestions[0] in lead_headers else 0,
                    key="lead_linkedin"
                )
            
            with c3:
                st.markdown("**First Name**")
                mapping['delivery_first'] = st.selectbox(
                    "From Delivery File", ["Not Available"] + delivery_headers,
                    index=1 if first_suggestions and first_suggestions[0] in delivery_headers else 0,
                    key="del_first"
                )
                mapping['lead_first'] = st.selectbox(
                    "From Lead File", ["Not Available"] + lead_headers,
                    index=1 if first_suggestions and first_suggestions[0] in lead_headers else 0,
                    key="lead_first"
                )
            
            with c4:
                st.markdown("**Last Name**")
                mapping['delivery_last'] = st.selectbox(
                    "From Delivery File", ["Not Available"] + delivery_headers,
                    index=1 if last_suggestions and last_suggestions[0] in delivery_headers else 0,
                    key="del_last"
                )
                mapping['lead_last'] = st.selectbox(
                    "From Lead File", ["Not Available"] + lead_headers,
                    index=1 if last_suggestions and last_suggestions[0] in lead_headers else 0,
                    key="lead_last"
                )

            # Domain for permutations (only if CPC not enabled, since CPC already has domain mapping)
            if not check_cpc:
                st.markdown("**Domain (for email permutations)**")
                d1, d2 = st.columns(2)
                with d1:
                    mapping['delivery_domain'] = st.selectbox(
                        "From Delivery File", ["Not Available"] + delivery_headers,
                        index=1 if domain_suggestions and domain_suggestions[0] in delivery_headers else 0,
                        key="del_domain_dup"
                    )
                with d2:
                    mapping['lead_domain'] = st.selectbox(
                        "From Lead File", ["Not Available"] + lead_headers,
                        index=1 if domain_suggestions and domain_suggestions[0] in lead_headers else 0,
                        key="lead_domain_dup"
                    )

        # Phone Mapping
        if check_phone:
            st.markdown("#### Phone Conflict Column Mapping")
            p1, p2 = st.columns(2)
            
            with p1:
                st.markdown("**Phone Number**")
                mapping['delivery_phone'] = st.selectbox(
                    "From Delivery File", ["Not Available"] + delivery_headers,
                    index=1 if phone_suggestions and phone_suggestions[0] in delivery_headers else 0,
                    key="del_phone"
                )
            
            with p2:
                st.markdown("**Phone Number**")
                mapping['lead_phone'] = st.selectbox(
                    "From Lead File", ["Not Available"] + lead_headers,
                    index=1 if phone_suggestions and phone_suggestions[0] in lead_headers else 0,
                    key="lead_phone"
                )
            
            # If CPC is not enabled, we need company and domain mapping for phone conflicts
            if not check_cpc:
                st.markdown("**Company & Domain (for phone conflicts)**")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Company Name**")
                    mapping['delivery_company'] = st.selectbox(
                        "From Delivery File", ["Not Available"] + delivery_headers,
                        index=1 if company_suggestions and company_suggestions[0] in delivery_headers else 0,
                        key="del_company_phone"
                    )
                    mapping['lead_company'] = st.selectbox(
                        "From Lead File", ["Not Available"] + lead_headers,
                        index=1 if company_suggestions and company_suggestions[0] in lead_headers else 0,
                        key="lead_company_phone"
                    )
                
                with c2:
                    st.markdown("**Domain**")
                    mapping['delivery_domain'] = st.selectbox(
                        "From Delivery File", ["Not Available"] + delivery_headers,
                        index=1 if domain_suggestions and domain_suggestions[0] in delivery_headers else 0,
                        key="del_domain_phone"
                    )
                    mapping['lead_domain'] = st.selectbox(
                        "From Lead File", ["Not Available"] + lead_headers,
                        index=1 if domain_suggestions and domain_suggestions[0] in lead_headers else 0,
                        key="lead_domain_phone"
                    )

        return mapping