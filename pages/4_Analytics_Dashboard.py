"""
Inspectra Analytics Dashboard
A Streamlit application for comprehensive lead data analytics with interactive visualizations.
Refactored Version - Enhanced UX with tabbed interface and improved visualizations.
"""

import streamlit as st
import logging
from typing import Dict, List, Any, Optional
from datetime import date
import plotly.graph_objects as go
import pandas as pd

# Import helper modules
from Analytics_Helper import (
    Config,
    ChartConfig,
    FileProcessingError,
    SheetNotFoundError,
    DataProcessor,
    DataValidator,
    AnalyticsGenerator,
    ChartGenerator,
    PDFExporter,
    FileSelector
)

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class AnalyticsDashboardApp:
    """Main application class for Analytics Dashboard."""
    
    def __init__(self):
        self.config = Config()
        self.chart_config = ChartConfig()
        self.processor = DataProcessor(self.config)
        self.validator = DataValidator(self.config)
        self.analytics_generator = AnalyticsGenerator()
        self.chart_generator = ChartGenerator(self.chart_config)
        self.pdf_exporter = PDFExporter(self.config)
    
    def run(self) -> None:
        """Run the Streamlit application."""
        st.set_page_config(
            page_title="Inspectra Analytics Dashboard",
            page_icon="📊",
            layout="wide"
        )
        
        self._add_custom_styling()
        self._render_hero_section()
        
        # Step 1: File Upload
        uploaded_file = self._render_file_upload_section()
        
        if not uploaded_file:
            self._show_instructions()
            return
        
        try:
            # Check if we need to process the file
            file_identifier = uploaded_file.name if uploaded_file else None
            cache_valid = (
                'processed_data' in st.session_state and 
                st.session_state.get('uploaded_file_name') == file_identifier
            )
            
            if not cache_valid:
                # Reset all session state for new file
                self._reset_session_state()
                
                with st.spinner("Processing Excel file..."):
                    # Load all sheets
                    sheet_names, sheet_counts = self.processor.load_excel_file(uploaded_file)
                    
                    # Step 2: Validate required sheets
                    is_valid, missing_sheets = self.processor.validate_required_sheets(sheet_names)
                    if not is_valid:
                        st.error(f"❌ Missing required sheets: {', '.join(missing_sheets)}")
                        st.info("📝 Required sheets: 'Qualified' and 'Disqualified' must be present in the Excel file.")
                        return
                    
                    st.success("✅ Required sheets validated successfully!")
                    
                    # Load and parse Qualified/Disqualified sheets
                    qualified_records, disqualified_records = self.processor.load_and_parse_sheets(uploaded_file)
                    combined_records = self.processor.get_combined_records()
                    
                    # Check available columns
                    headers = self.processor.get_column_headers(combined_records)
                    optional_columns = self.processor.check_optional_columns(headers)
                    available_custom_columns = self.processor.get_available_columns_for_custom_report(combined_records)
                    
                    # Store in session state (before corrections)
                    st.session_state.processed_data = {
                        'sheet_names': sheet_names,
                        'sheet_counts': sheet_counts,
                        'combined_records': combined_records,
                        'headers': headers,
                        'optional_columns': optional_columns,
                        'available_custom_columns': available_custom_columns
                    }
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.session_state.file_validated = True
            
            # Get processed data from session state
            processed_data = st.session_state.processed_data
            combined_records = processed_data['combined_records']
            
            # Step 3: Lead Status Correction Interface
            if not st.session_state.get('correction_decision_made', False):
                issues, auto_suggestions = self.validator.find_lead_status_issues(combined_records)
                
                if issues:
                    st.markdown("---")
                    st.warning(f"⚠️ Found {len(issues)} Lead Status values that need correction")
                    
                    user_corrections = self._show_correction_interface(issues)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Apply Corrections & Continue", type="primary", use_container_width=True):
                            with st.spinner("Applying corrections..."):
                                corrected_records, correction_count = self.validator.apply_corrections(
                                    combined_records, user_corrections
                                )
                                # Clean corrected data
                                cleaned_records = self.processor.clean_data(corrected_records)
                                st.session_state.processed_data['combined_records'] = cleaned_records
                            
                            st.success(f"✅ Applied {len(user_corrections)} corrections to {correction_count} records!")
                            st.session_state.correction_decision_made = True
                            st.session_state.corrections_applied = True
                            st.session_state.correction_summary = self.validator.get_correction_summary()
                            st.rerun()
                    
                    with col2:
                        if st.button("⏭️ Skip Corrections & Continue", type="secondary", use_container_width=True):
                            # Clean data without corrections
                            cleaned_records = self.processor.clean_data(combined_records)
                            st.session_state.processed_data['combined_records'] = cleaned_records
                            st.session_state.correction_decision_made = True
                            st.session_state.corrections_applied = False
                            st.rerun()
                    
                    return
                else:
                    # No issues found, proceed with cleaning
                    if not st.session_state.get('correction_decision_made', False):
                        cleaned_records = self.processor.clean_data(combined_records)
                        st.session_state.processed_data['combined_records'] = cleaned_records
                        st.session_state.correction_decision_made = True
                        st.session_state.corrections_applied = False
            
            # Update combined_records after correction decision
            processed_data = st.session_state.processed_data
            combined_records = processed_data['combined_records']
            sheet_counts = processed_data['sheet_counts']
            headers = processed_data['headers']
            optional_columns = processed_data['optional_columns']
            available_custom_columns = processed_data['available_custom_columns']
            
            # Show correction status
            if st.session_state.get('corrections_applied'):
                st.info("ℹ️ Data corrections have been applied")
                with st.expander("View Correction Summary"):
                    st.text(st.session_state.get('correction_summary', ''))
            
            # Step 4: Overall Summary (Always visible)
            st.markdown("---")
            self._show_overall_summary(combined_records)
            
            # Show Sheet Wise Data Count (file-level info) — this stays
            st.markdown("---")
            st.markdown('<div class="section-title">📋 Sheet Wise Data Count</div>', unsafe_allow_html=True)
            sheet_wise_count = self.analytics_generator.generate_sheet_wise_count(sheet_counts)
            self._display_table(sheet_wise_count)
            
            # Step 5: Date Selection Section
            st.markdown("---")
            st.markdown('<div class="section-title">📊 Select Analytics Mode</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🌍 All Time Analytics", type="primary", use_container_width=True):
                    st.session_state.analytics_mode = "all_time"
                    st.session_state.analytics_mode_selected = True
                    if 'analytics_results' in st.session_state:
                        del st.session_state.analytics_results
                    st.rerun()
            
            with col2:
                if st.button("📅 Date Wise Analytics", type="secondary", use_container_width=True):
                    st.session_state.analytics_mode = "date_wise"
                    st.session_state.analytics_mode_selected = True
                    if 'analytics_results' in st.session_state:
                        del st.session_state.analytics_results
                    st.rerun()
            
            # Show analytics options based on selected mode
            if st.session_state.get('analytics_mode_selected', False):
                analytics_mode = st.session_state.get('analytics_mode')
                
                if analytics_mode == "date_wise":
                    # Date selection
                    unique_dates = self.processor.get_unique_dates(combined_records, "Audit Date")
                    
                    if not unique_dates:
                        st.error("❌ No valid dates found in 'Audit Date' column")
                        return
                    
                    st.markdown("---")
                    selected_date = st.selectbox(
                        "📅 Select Date",
                        options=unique_dates,
                        format_func=lambda x: x.strftime("%d-%b-%Y"),
                        key="selected_audit_date"
                    )
                    
                    if selected_date:
                        st.session_state.selected_date = selected_date
                        filtered_records = self.processor.filter_records_by_date(
                            combined_records, selected_date, "Audit Date"
                        )
                        
                        if not filtered_records:
                            st.warning(f"⚠️ No records found for {selected_date.strftime('%d-%b-%Y')}")
                            return
                        
                        st.info(f"📊 Analyzing {len(filtered_records):,} records for {selected_date.strftime('%d-%b-%Y')}")
                        records_to_analyze = filtered_records
                    else:
                        return
                else:
                    # All time analytics
                    records_to_analyze = combined_records
                    st.info(f"📊 Analyzing all {len(records_to_analyze):,} records")
                
                # Optional custom column report selection
                st.markdown("---")
                st.markdown('<div class="section-title">⚙️ Optional Reports</div>', unsafe_allow_html=True)
                
                # Email Status Column Selection
                email_status_column = None
                if 'Email Status 1' in headers:
                    email_status_column = 'Email Status 1'
                    st.info("✓ Email Status 1 column detected - will generate Email Status analytics")
                else:
                    email_cols = [h for h in headers if 'email' in h.lower() and 'sta' in h.lower()]
                    if email_cols:
                        st.warning(f"⚠️ 'Email Status 1' not found, but found: {', '.join(email_cols)}")
                        email_status_column = st.selectbox(
                            "Select Email Status Column",
                            options=email_cols,
                            key="email_status_selector",
                            help="Select the column containing email status data"
                        )
                        if email_status_column:
                            st.success(f"✓ Will use '{email_status_column}' for Email Status analytics")
                
                st.markdown("---")
                
                # Custom Column Report (Qualified/Disqualified breakdown) — still available
                enable_custom_report = st.checkbox(
                    "📋 Enable Custom Column Report (Qualified/Disqualified)",
                    help="Generate qualified and disqualified count report for any column"
                )
                
                selected_custom_column = None
                if enable_custom_report and available_custom_columns:
                    selected_custom_column = st.selectbox(
                        "Select Column for Custom Report",
                        options=available_custom_columns,
                        key="custom_column_selector"
                    )
                
                # NOTE: Sheet Wise Custom Report has been removed
                
                # Generate Analytics button
                st.markdown("---")
                if st.button("🚀 Generate Analytics", type="primary", use_container_width=True):
                    self._generate_analytics(
                        sheet_counts,
                        records_to_analyze,
                        optional_columns,
                        selected_custom_column,
                        analytics_mode,
                        email_status_column,
                    )
                    st.rerun()
                
                # Step 6: Display analytics in tabs if already generated
                if 'analytics_results' in st.session_state:
                    st.markdown("---")
                    self._display_tabbed_analytics()
                    
                    # Step 7: PDF Export section
                    st.markdown("---")
                    self._show_download_section()
        
        except FileProcessingError as e:
            st.error(f"❌ File Processing Error: {str(e)}")
        except SheetNotFoundError as e:
            st.error(f"❌ Sheet Error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Unexpected Error: {str(e)}")
            logger.exception("Unexpected error in main application")
    
    def _reset_session_state(self):
        """Reset session state for new file upload."""
        keys_to_keep = ['network_file']  # Keep network file selection
        keys_to_remove = [k for k in st.session_state.keys() if k not in keys_to_keep]
        for key in keys_to_remove:
            del st.session_state[key]
    
    def _add_custom_styling(self) -> None:
        """Add custom CSS styling."""
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
    
    def _render_hero_section(self) -> None:
        """Render the hero section."""
        st.markdown("""
        <div class="inspectra-hero">
            <div class="inspectra-inline">
                <span class="inspectra-title">Inspectra</span>
                <span class="inspectra-divider">|</span>
                <span class="inspectra-tagline">Analytics</span>
            </div>
        </div>
        <div class="section">
            <div class="section-title">📊 What is this?</div>
            <b>Inspectra Analytics</b> is a powerful tool to generate comprehensive Analytics reports from lead data.<br>
            Upload your Excel file or Select File From Shared Network Drive.
        </div>
        """, unsafe_allow_html=True)
    
    def _render_file_upload_section(self) -> Optional[Any]:
        """Render file upload section with network path option."""
        st.markdown('<div class="section-title">📁 Upload Data File</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["💻 Local Upload", "🌐 Network Path"])
        
        with tab1:
            uploaded_file = st.file_uploader(
                "Choose Excel file",
                type=['xlsx', 'xlsm'],
                help="Upload Excel file with Qualified and Disqualified sheets"
            )
            if uploaded_file:
                st.success(f"✅ Loaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
                return uploaded_file
        
        with tab2:
            file_selector = FileSelector()
            
            if not file_selector.path_exists():
                st.error(f"❌ Network path not accessible: {file_selector.base_dir}")
                st.info("💡 Please check network connection or use Local Upload")
                return None
            
            months = file_selector.get_month_folders()
            if not months:
                st.warning("⚠️ No month folders found")
                return None
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_month = st.selectbox("📅 Month", months, key="network_month")
            
            campaigns = file_selector.get_campaign_folders(selected_month) if selected_month else []
            
            with col2:
                if not campaigns:
                    st.warning("No campaigns found")
                    return None
                selected_campaign = st.selectbox("📋 Campaign", campaigns, key="network_campaign")
            
            files = file_selector.get_excel_files(selected_month, selected_campaign) if selected_campaign else []
            
            if not files:
                st.warning("No Excel files found")
                return None
            
            file_options = []
            for filename, filepath, mod_time, size_mb in files:
                display = file_selector.get_file_display_name(filename, mod_time, size_mb)
                file_options.append((display, filename, filepath))
            
            with col3:
                selected_display = st.selectbox(
                    "📄 Select Excel File",
                    [opt[0] for opt in file_options],
                    key="network_file_display"
                )
            
            if not selected_display:
                return None
            
            _, filename, filepath = next(x for x in file_options if x[0] == selected_display)
            
            st.info(f"📂 Path: `{selected_month}` → `{selected_campaign}` → `{filename}`")
            
            if st.button("📥 Load File", type="primary"):
                with st.spinner("Reading file…"):
                    try:
                        content = file_selector.read_file(filepath)
                        import io
                        uploaded_file = io.BytesIO(content)
                        uploaded_file.name = filename
                        uploaded_file.size = len(content)
                        
                        st.success(f"Loaded: {filename}")
                        st.session_state.network_file = uploaded_file
                        return uploaded_file
                    
                    except Exception as e:
                        st.error(f"❌ Error reading file: {e}")
                        return None
            
            return st.session_state.get("network_file")
        
        return None
    
    def _show_instructions(self) -> None:
        """Display instructions when no file is uploaded."""
        st.info("👆 Please upload an Excel file to begin analytics")
        
        with st.expander("📖 How to Use This Dashboard"):
            st.markdown("""
            **Requirements:**
            1. Excel file must contain **Qualified** and **Disqualified** sheets
            2. Required columns: **Lead Status**, **Audit Date**
            3. Optional columns: **Segment Tagging**, **Email Status 1**, **DQ Reason**
            
            **Features:**
            - ✅ Automatic sheet validation
            - 🔧 Optional Lead Status correction
            - 📊 Overall summary with qualified/disqualified counts
            - 📈 Interactive tabbed analytics interface
            - 📅 All-time or date-wise filtering
            - 📄 Professional PDF report download
            
            **Steps:**
            1. Upload your Excel file (local or network path)
            2. System validates required sheets
            3. Optionally correct Lead Status issues
            4. View overall summary
            5. Select analytics mode (All Time or Date Wise)
            6. Generate analytics (displayed in tabs)
            7. Download PDF report with Campaign ID
            """)
    
    def _show_overall_summary(self, records: List[Dict[str, Any]]) -> None:
        """Display overall qualified and disqualified summary."""
        st.markdown('<div class="section-title">📊 Overall Summary</div>', unsafe_allow_html=True)
        
        total_records = len(records)
        qualified_count = sum(1 for r in records if self.processor.normalize(r.get("Lead Status", "")) == "qualified")
        disqualified_count = sum(1 for r in records if self.processor.normalize(r.get("Lead Status", "")) == "disqualified")
        
        qualified_pct = (qualified_count / total_records * 100) if total_records > 0 else 0
        disqualified_pct = (disqualified_count / total_records * 100) if total_records > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", f"{total_records:,}")
        
        with col2:
            st.metric(
                "Qualified", 
                f"{qualified_count:,}", 
                delta=f"{qualified_pct:.1f}%",
                delta_color="normal"
            )
        
        with col3:
            st.metric(
                "Disqualified", 
                f"{disqualified_count:,}", 
                delta=f"{disqualified_pct:.1f}%",
                delta_color="inverse"
            )
    
    def _show_correction_interface(self, issues: List[Dict]) -> Dict[str, str]:
        """Show Lead Status correction interface."""
        st.markdown("### 🔧 Lead Status Correction")
        
        user_corrections = {}
        
        for issue in issues:
            original = issue['original']
            count = issue['count']
            auto_suggestion = issue['auto_suggestion']
            
            st.markdown(f"**Invalid value:** `{original}` ({count} records)")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if auto_suggestion:
                    correction = st.selectbox(
                        f"Correct to:",
                        options=[auto_suggestion] + [opt for opt in issue['valid_options'] if opt != auto_suggestion],
                        key=f"correction_{original}"
                    )
                else:
                    correction = st.selectbox(
                        f"Correct to:",
                        options=issue['valid_options'],
                        key=f"correction_{original}"
                    )
                
                user_corrections[original] = correction
            
            with col2:
                if auto_suggestion:
                    st.success("✨ Auto")
        
        return user_corrections
    
    def _generate_analytics(
        self,
        sheet_counts: Dict[str, int],
        records: List[Dict[str, Any]],
        optional_columns: Dict[str, bool],
        custom_column: Optional[str],
        analytics_mode: str,
        email_status_column: Optional[str] = None,
    ) -> None:
        """Generate all analytics data and charts."""
        with st.spinner("🔄 Generating analytics..."):
            analytics_data = {}
            charts = {}
            available_analytics = []

            # 1. Segment-wise analysis
            has_segment = "Segment Tagging" in records[0] if records else False
            if has_segment:
                segment_table = self.analytics_generator.generate_segment_wise_analysis(
                    records
                )
                analytics_data["segment_wise_analysis"] = segment_table
                # Pie chart for segments
                charts["segment_pie_chart"] = self.chart_generator.create_segment_pie_chart(
                    segment_table
                )
                available_analytics.append("Segment Wise Analysis")

            # 2. Qualified vs Disqualified
            qual_disqual_summary = (
                self.analytics_generator.generate_qualified_disqualified_summary(records)
            )
            charts["qualified_disqualified_chart"] = (
                self.chart_generator.create_qualified_disqualified_bar_chart(
                    qual_disqual_summary
                )
            )
            charts["qualified_disqualified_pie"] = (
                self.chart_generator.create_qualified_disqualified_pie_chart(
                    qual_disqual_summary
                )
            )
            available_analytics.append("Qualified vs Disqualified")

            # 3. DQ Reason analytics
            has_dq_reason = "DQ Reason" in records[0] if records else False
            if has_dq_reason:
                dq_table, dq_counts = (
                    self.analytics_generator.generate_dq_reason_analytics(records)
                )
                analytics_data["dq_reason_table"] = dq_table
                if dq_counts:
                    charts["dq_reason_chart"] = (
                        self.chart_generator.create_dq_reason_bar_chart(dq_counts)
                    )
                    charts["dq_reason_pie_chart"] = (
                        self.chart_generator.create_dq_reason_pie_chart(dq_counts)
                    )
                available_analytics.append("DQ Reason Analytics")

            # 4. Email Status
            if email_status_column:
                email_status_counts = self.analytics_generator.generate_email_status_qualified_count_dynamic(
                    records, email_status_column
                )
                if email_status_counts:
                    charts["email_status_chart"] = (
                        self.chart_generator.create_email_status_donut_chart(
                            email_status_counts
                        )
                    )
                    available_analytics.append(
                        f"Email Status Analysis ({email_status_column})"
                    )

            # 5. Custom column report (Qualified/Disqualified breakdown)
            if custom_column:
                analytics_data["custom_column_report"] = (
                    self.analytics_generator.generate_custom_column_qualified_count(
                        records, custom_column
                    )
                )
                analytics_data["custom_column_name"] = custom_column
                available_analytics.append(f"{custom_column} Analysis")

            # 6. Summary statistics
            analytics_data["summary_stats"] = (
                self.analytics_generator.generate_summary_statistics(records)
            )
            # Also include sheet-wise count for PDF
            analytics_data["sheet_wise_count"] = self.analytics_generator.generate_sheet_wise_count(
                sheet_counts
            )

            # Store in session state
            st.session_state.analytics_results = {
                "analytics_data": analytics_data,
                "charts": charts,
                "analytics_mode": analytics_mode,
                "record_count": len(records),
                "available_analytics": available_analytics,
            }

        st.success("✅ Analytics generated successfully!")
    
    def _display_tabbed_analytics(self) -> None:
        """Display analytics in tabbed interface."""
        results = st.session_state.analytics_results
        analytics_data = results['analytics_data']
        charts = results['charts']
        analytics_mode = results['analytics_mode']
        record_count = results['record_count']
        
        # Display mode info
        if analytics_mode == "all_time":
            mode_text = "All Time Analytics"
        else:
            selected_date = st.session_state.get('selected_date', None)
            if selected_date:
                mode_text = f"Date Wise Analytics ({selected_date.strftime('%d-%b-%Y')})"
            else:
                mode_text = "Date Wise Analytics"
        st.info(f"📊 {mode_text} | Records Analyzed: {record_count:,}")
        
        # Create tabs
        tab_names = ["📊 Overview", "🎯 Segment Analysis", "📉 DQ Analysis"]
        
        # Conditionally add tabs
        if 'email_status_chart' in charts:
            tab_names.append("📧 Email Status")
        
        # Custom Reports tab only if custom_column_report exists
        if 'custom_column_report' in analytics_data:
            tab_names.append("🔧 Custom Reports")
        
        tabs = st.tabs(tab_names)
        
        # Tab 1: Overview
        with tabs[0]:
            self._render_overview_tab(analytics_data, charts)
        
        # Tab 2: Segment Analysis
        with tabs[1]:
            self._render_segment_tab(analytics_data, charts)

        # Tab 3: DQ Analysis
        with tabs[2]:
            self._render_dq_analysis_tab(analytics_data, charts)
        
        tab_idx = 3
        
        # Tab 4: Email Status (if available)
        if 'email_status_chart' in charts:
            with tabs[tab_idx]:
                self._render_email_status_tab(charts)
            tab_idx += 1
        
        # Tab 5: Custom Reports (if available)
        if 'custom_column_report' in analytics_data:
            with tabs[tab_idx]:
                self._render_custom_reports_tab(analytics_data)
    
    def _render_overview_tab(self, analytics_data: Dict, charts: Dict) -> None:
        """Render overview tab with summary metrics and sub-tabs for table/chart."""
        st.markdown("### 📊 Overview Dashboard")

        # --- Summary KPIs ---
        if "summary_stats" in analytics_data:
            stats = analytics_data["summary_stats"]
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Records", f"{stats['total_records']:,}")

            with col2:
                st.metric(
                    "Qualified",
                    f"{stats['qualified_count']:,}",
                    f"{stats['qualified_rate']:.1f}%"
                )

            with col3:
                st.metric(
                    "Disqualified",
                    f"{stats['disqualified_count']:,}",
                    f"{stats['disqualified_rate']:.1f}%"
                )

            with col4:
                st.metric(
                    "Qualification Rate",
                    f"{stats['qualified_rate']:.1f}%"
                )

        st.markdown("---")

        # --- Sub-tabs for Table / Chart ---
        tab_table, tab_chart = st.tabs(["📋 Table View", "📊 Chart View"])

        # TABLE SUB-TAB
        with tab_table:
            st.markdown("#### 📋 Qualified vs Disqualified Summary")

            summary = analytics_data.get("summary_stats", {})
            if summary:
                table_data = [
                    ["Status", "Count"],
                    ["Qualified", summary.get("qualified_count", 0)],
                    ["Disqualified", summary.get("disqualified_count", 0)],
                    ["Total", summary.get("total_records", 0)]
                ]

                headers = table_data[0]
                rows = table_data[1:]

                df = pd.DataFrame(rows, columns=headers)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No summary data available.")

        # CHART SUB-TAB
        with tab_chart:
            st.markdown("#### 📊 Qualified vs Disqualified (Bar Chart)")
            if "qualified_disqualified_chart" in charts:
                st.plotly_chart(
                    charts["qualified_disqualified_chart"],
                    use_container_width=True
                )
            else:
                st.info("No chart available.")
    
    def _render_segment_tab(self, analytics_data: Dict, charts: Dict) -> None:
        """Render segment analysis tab with table + chart sub-tabs."""
        if "segment_wise_analysis" not in analytics_data:
            st.info("ℹ️ Segment Tagging column not found in data")
            return

        st.markdown("### 🎯 Segment Wise Analysis")

        tab_table, tab_chart = st.tabs(["📋 Table", "📊 Chart"])

        with tab_table:
            self._display_table(analytics_data["segment_wise_analysis"])

        with tab_chart:
            if "segment_pie_chart" in charts:
                st.plotly_chart(
                    charts["segment_pie_chart"], use_container_width=True
                )
            else:
                st.info("ℹ️ No chart available for segment analysis.")
    
    def _render_dq_analysis_tab(self, analytics_data: Dict, charts: Dict) -> None:
        """Render DQ analysis tab with table + chart sub-tabs."""
        if "dq_reason_table" not in analytics_data:
            st.info("ℹ️ DQ Reason column not found in data")
            return

        st.markdown("### 📉 DQ Reason Analytics")

        tab_chart, tab_table = st.tabs(["📊 Charts", "📋 Table"])

        with tab_chart:
            if "dq_reason_chart" in charts:
                st.markdown("#### 📊 Top DQ Reasons (Bar)")
                st.plotly_chart(
                    charts["dq_reason_chart"], use_container_width=True
                )

            if "dq_reason_pie_chart" in charts:
                st.markdown("#### 🥧 Top DQ Reasons (Pie)")
                st.plotly_chart(
                    charts["dq_reason_pie_chart"], use_container_width=True
                )

            if "dq_reason_chart" not in charts and "dq_reason_pie_chart" not in charts:
                st.info("ℹ️ No charts available for DQ Reason analysis.")

        with tab_table:
            st.markdown("#### 📊 Detailed DQ Reason Breakdown")
            self._display_table(analytics_data["dq_reason_table"])
    
    def _render_email_status_tab(self, charts: Dict) -> None:
        """Render email status tab."""
        st.markdown("### 📧 Email Status - Qualified Leads")
        
        if 'email_status_chart' in charts:
            st.plotly_chart(charts['email_status_chart'], use_container_width=True)
    
    def _render_custom_reports_tab(self, analytics_data: Dict) -> None:
        """Render custom reports tab - only custom column report remains."""
        st.markdown("### 🔧 Custom Reports")
        
        # Custom Column Report (Qualified/Disqualified breakdown)
        if 'custom_column_report' in analytics_data:
            column_name = analytics_data.get('custom_column_name', 'Custom Column')
            st.markdown(f"#### 📋 {column_name} Analysis (Qualified/Disqualified)")
            st.info("This report shows the breakdown of Qualified and Disqualified counts for each value.")
            self._display_table(analytics_data['custom_column_report'])
        else:
            st.info("ℹ️ No custom reports generated.")
    
    def _display_table(self, table_data: List[List[Any]]) -> None:
        """Display table using Streamlit's dataframe for a more modern look."""
        if not table_data or len(table_data) < 2:
            st.info("No data available")
            return

        headers = table_data[0]
        rows = table_data[1:]

        df = pd.DataFrame(rows, columns=headers)

        # Simple, clean interactive table
        st.dataframe(df, use_container_width=True)
    
    def _show_download_section(self) -> None:
        """Show download section with campaign ID input."""
        st.markdown('<div class="section-title">📥 Download PDF Report</div>', unsafe_allow_html=True)
        
        campaign_id = st.text_input(
            "Campaign ID",
            placeholder="Enter campaign ID (e.g., CAMP_2024_001)",
            help="Enter the campaign ID for the PDF report",
            key="campaign_id_input"
        )
        
        if campaign_id.strip():
            campaign_id = campaign_id.strip()
            
            if campaign_id.replace('_', '').replace('-', '').isalnum():
                st.success(f"✅ Campaign ID: {campaign_id}")
                
                if st.button("📄 Generate & Download PDF Report", type="primary"):
                    self._generate_pdf_report(campaign_id)
            else:
                st.warning("⚠️ Campaign ID should contain only letters, numbers, underscores, and hyphens")
        else:
            st.info("💡 Enter a Campaign ID above to generate PDF report")
    
    def _generate_pdf_report(self, campaign_id: str) -> None:
        """Generate and download PDF report."""
        try:
            with st.spinner("📄 Generating PDF report..."):
                results = st.session_state.analytics_results
                analytics_data = results['analytics_data']
                charts = results['charts']
                
                pdf_bytes = self.pdf_exporter.create_pdf_report(
                    campaign_id=campaign_id,
                    analytics_data=analytics_data,
                    charts=charts
                )
                
                # Get filename
                analytics_mode = results['analytics_mode']
                if analytics_mode == "date_wise":
                    selected_date = st.session_state.get('selected_date')
                    filename = f"Inspectra_Analytics_{campaign_id}_{selected_date.strftime('%d%b%y')}.pdf"
                else:
                    filename = f"Inspectra_Analytics_{campaign_id}_AllTime.pdf"
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    type="primary"
                )
                
                st.success("✅ PDF report generated successfully!")
        
        except Exception as e:
            st.error(f"❌ Error generating PDF: {str(e)}")
            logger.exception("Error generating PDF report")


def main():
    """Application entry point."""
    app = AnalyticsDashboardApp()
    app.run()
    
    st.markdown("""
    <hr style="margin-top: 3rem; margin-bottom: 1rem;">
    <div style='text-align: center; font-size: 14px; color: #6c757d;'>
        2025 Interlink. All rights reserved. <br>Built by Felix Markas Salve as an internal innovation project.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
