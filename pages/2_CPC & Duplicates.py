import streamlit as st
import tempfile
import os
import logging
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager

# Import modular components
from CPC_Duplicate_Helper import DataProcessor, UIComponents, FileHandler
from CPC_Duplicate_Helper.validation_helpers import get_validation_errors

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def loading_spinner(message: str):
    """Context manager for loading spinner with logging"""
    logger.info(f"Starting: {message}")
    with st.spinner(message):
        yield
    logger.info(f"Completed: {message}")

class CPCDuplicateChecker:
    """Main class for CPC and Duplicate checking functionality"""
    
    def __init__(self):
        self.initialize_session_state()
        self.load_css()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        defaults = {
            'delivery_file': None,
            'lead_file': None,
            'cpc_limit': 3,
            'temp_output_file': None,
            'temp_summary_file': None,
            'processing_history': []
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def load_css():
        """Load custom CSS with error handling"""
        try:
            with open("styles/inspectra.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            logger.warning("CSS file not found, using default styling")
        except Exception as e:
            logger.error(f"Error loading CSS: {e}")

    def cleanup_temp_files(self) -> bool:
        """Clean up temporary files with improved error handling"""
        cleaned = False
        
        for file_key in ['temp_output_file', 'temp_summary_file']:
            file_path = st.session_state.get(file_key)
            if file_path and os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                    st.session_state[file_key] = None
                    cleaned = True
                    logger.info(f"Cleaned up temporary file: {file_path}")
                except Exception as e:
                    logger.error(f"Error cleaning up {file_path}: {e}")
        
        return cleaned

    def generate_summary_report(self, stats: Dict, checks: Dict, is_first_delivery: bool) -> str:
        """Generate comprehensive summary report with enhanced formatting"""
        mode_text = "Internal Validation" if is_first_delivery else "Full Validation"
        
        # Header section
        report_lines = [
            f"CPC & Duplicate Check Report - {mode_text}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 50,
            ""
        ]
        
        # Files processed section
        if is_first_delivery:
            report_lines.extend([
                "Files Processed:",
                f"  Lead: {st.session_state.lead_file.name}",
                ""
            ])
        else:
            report_lines.extend([
                "Files Processed:",
                f"  Delivery: {st.session_state.delivery_file.name}",
                f"  Lead: {st.session_state.lead_file.name}",
                ""
            ])
        
        # Summary statistics
        report_lines.extend([
            "Summary:",
            f"  Total Leads: {stats['total_leads']:,}",
            f"  Passed: {stats['passed']:,}"
        ])
        
        # Add violation details based on enabled checks
        violation_details = self._get_violation_details(stats, checks, is_first_delivery)
        report_lines.extend(violation_details)
        
        # Performance metrics
        report_lines.extend([
            f"  Processing Time: {stats['processing_time']:.2f} seconds",
            f"  Processing Rate: {stats['total_leads']/max(stats['processing_time'], 0.1):.0f} rows/second"
        ])
        
        # Company analysis
        company_details = self._get_company_analysis(stats)
        if company_details:
            report_lines.extend([""] + company_details)
        
        # Error summary
        if stats.get('permutation_errors', 0) > 0:
            report_lines.extend([
                "",
                f"Note: {stats['permutation_errors']} email permutation errors encountered"
            ])
        
        return "\n".join(report_lines)
    
    def _get_violation_details(self, stats: Dict, checks: Dict, is_first_delivery: bool) -> List[str]:
        """Get violation details for the report"""
        details = []
        
        if checks['check_cpc']:
            if not is_first_delivery:
                details.append(f"  External CPC Violations: {stats['cpc_violations']:,}")
            details.append(f"  Internal CPC Violations: {stats.get('internal_cpc_violations', 0):,}")
        
        if checks['check_duplicates']:
            if not is_first_delivery:
                details.append(f"  External Duplicates: {stats['duplicates_found']:,}")
            details.append(f"  Internal Duplicates: {stats.get('internal_duplicates', 0):,}")
        
        if checks['check_phone']:
            if not is_first_delivery:
                details.append(f"  External Phone Conflicts: {stats['phone_conflicts']:,}")
            details.append(f"  Internal Phone Conflicts: {stats.get('internal_phone_conflicts', 0):,}")
        
        return details
    
    def _get_company_analysis(self, stats: Dict) -> Optional[List[str]]:
        """Get company analysis details for the report"""
        details = []
        
        if stats.get('internal_companies_checked'):
            details.append(f"Unique Companies Checked (Internal): {len(stats['internal_companies_checked'])}")
        
        if stats.get('companies_checked'):
            details.append(f"Unique Companies Checked (External): {len(stats['companies_checked'])}")
        
        return details if details else None

    def display_results(self, stats: Dict, checks: Dict, output_file_path: str, 
                       summary_file_path: str, is_first_delivery: bool):
        """Display comprehensive results with enhanced UI"""
        mode_text = "Internal Validation" if is_first_delivery else "Full Validation"
        
        # Success message with processing time
        st.success(f"✅ {mode_text} Complete! (Processed in {stats['processing_time']:.1f} seconds)")
        
        # Main metrics dashboard
        self._display_main_metrics(stats, is_first_delivery)
        
        # Violation breakdown
        if any(checks.values()):
            self._display_violation_breakdown(stats, checks, is_first_delivery)
        
        # Detailed analysis sections
        self._display_detailed_analysis(stats, checks, is_first_delivery)
        
        # Download section
        self._display_download_section(output_file_path, summary_file_path)
        
        # Add to processing history
        self._add_to_history(stats, is_first_delivery)
    
    def _display_main_metrics(self, stats: Dict, is_first_delivery: bool):
        """Display main metrics dashboard"""
        st.markdown("### 📊 Results Summary")
        
        # Calculate key metrics
        pass_rate = (stats['passed'] / stats['total_leads'] * 100) if stats['total_leads'] > 0 else 0
        total_violations = self._calculate_total_violations(stats, is_first_delivery)
        viol_rate = (total_violations / stats['total_leads'] * 100) if stats['total_leads'] > 0 else 0
        
        # Main metrics columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Leads", f"{stats['total_leads']:,}")
        
        with col2:
            st.metric("Passed", f"{stats['passed']:,}", 
                     delta=f"{pass_rate:.1f}%", delta_color="normal")
        
        with col3:
            st.metric("Disqualified", f"{total_violations:,}", 
                     delta=f"-{viol_rate:.1f}%", delta_color="inverse")
        
        with col4:
            pass_rating = "Excellent" if pass_rate >= 90 else "Good" if pass_rate >= 80 else "Fair" if pass_rate >= 60 else "Poor"
            st.metric("Pass Rate", f"{pass_rate:.1f}%", delta=pass_rating,
                     delta_color="normal" if pass_rate >= 60 else "inverse")
    
    def _calculate_total_violations(self, stats: Dict, is_first_delivery: bool) -> int:
        """Calculate total violations across all checks"""
        if is_first_delivery:
            return (stats.get('internal_cpc_violations', 0) + 
                   stats.get('internal_duplicates', 0) + 
                   stats.get('internal_phone_conflicts', 0))
        else:
            return (stats.get('cpc_violations', 0) + 
                   stats.get('duplicates_found', 0) + 
                   stats.get('phone_conflicts', 0) +
                   stats.get('internal_duplicates', 0) + 
                   stats.get('internal_cpc_violations', 0) +
                   stats.get('internal_phone_conflicts', 0))
    
    def _display_violation_breakdown(self, stats: Dict, checks: Dict, is_first_delivery: bool):
        """Display detailed violation breakdown"""
        st.markdown("### 🔍 Violation Breakdown")
        
        breakdown_data = []
        
        if checks['check_cpc']:
            if not is_first_delivery and stats.get('cpc_violations', 0) > 0:
                breakdown_data.append(("External CPC Violations", stats['cpc_violations']))
            if stats.get('internal_cpc_violations', 0) > 0:
                breakdown_data.append(("Internal CPC Violations", stats['internal_cpc_violations']))
        
        if checks['check_duplicates']:
            if not is_first_delivery and stats.get('duplicates_found', 0) > 0:
                breakdown_data.append(("External Duplicates", stats['duplicates_found']))
            if stats.get('internal_duplicates', 0) > 0:
                breakdown_data.append(("Internal Duplicates", stats['internal_duplicates']))
        
        if checks['check_phone']:
            if not is_first_delivery and stats.get('phone_conflicts', 0) > 0:
                breakdown_data.append(("External Phone Conflicts", stats['phone_conflicts']))
            if stats.get('internal_phone_conflicts', 0) > 0:
                breakdown_data.append(("Internal Phone Conflicts", stats['internal_phone_conflicts']))
        
        if stats.get('permutation_errors', 0) > 0:
            breakdown_data.append(("Processing Errors", stats['permutation_errors']))
        
        # Display in columns
        cols = st.columns(min(len(breakdown_data), 6))
        for i, (label, value) in enumerate(breakdown_data):
            if i < len(cols):
                cols[i].metric(label, f"{value:,}")
    
    def _display_detailed_analysis(self, stats: Dict, checks: Dict, is_first_delivery: bool):
        """Display detailed analysis sections"""
        # Phone conflict analysis
        if checks['check_phone']:
            self._display_phone_analysis(stats, is_first_delivery)
        
        # Company analysis for CPC
        if checks['check_cpc']:
            self._display_company_analysis(stats, is_first_delivery)
        
        # Duplicate analysis
        if checks['check_duplicates']:
            self._display_duplicate_analysis(stats, is_first_delivery)
    
    def _display_phone_analysis(self, stats: Dict, is_first_delivery: bool):
        """Display phone conflict analysis"""
        # External phone conflicts
        if not is_first_delivery and stats.get('simple_phone_details'):
            phone_details = stats['simple_phone_details']
            if phone_details:
                st.markdown("#### 📞 External Phone Conflict Analysis")
                
                with st.expander(f"📋 External Phone Conflicts ({len(phone_details)} found)", expanded=False):
                    df_phone = self._create_phone_conflicts_df(phone_details, is_internal=False)
                    st.dataframe(df_phone, use_container_width=True, hide_index=True)
        
        # Internal phone conflicts
        if stats.get('internal_phone_details'):
            internal_phone_details = stats['internal_phone_details']
            if internal_phone_details:
                st.markdown("#### 📞 Internal Phone Conflict Analysis")
                
                with st.expander(f"📋 Internal Phone Conflicts ({len(internal_phone_details)} found)", expanded=False):
                    df_internal_phone = self._create_phone_conflicts_df(internal_phone_details, is_internal=True)
                    st.dataframe(df_internal_phone, use_container_width=True, hide_index=True)
    
    def _create_phone_conflicts_df(self, phone_details: List[Dict], is_internal: bool) -> pd.DataFrame:
        """Create DataFrame for phone conflicts display"""
        simplified_details = []
        
        for detail in phone_details:
            if is_internal:
                current_display = f"{detail['current_company']} ({detail['current_domain']})" if detail.get('current_domain') else detail['current_company']
                conflicting_display = f"{detail['conflicting_company']} ({detail['conflicting_domain']})" if detail.get('conflicting_domain') else detail['conflicting_company']
                
                simplified_details.append({
                    'Row': detail['row'],
                    'Phone': detail['phone'],
                    'Current Company': current_display,
                    'Conflicting Company': conflicting_display,
                    'Conflicting Row': detail['conflicting_row'],
                    'Issue': detail['conflict_message']
                })
            else:
                lead_display = f"{detail['lead_company']} ({detail['lead_domain']})" if detail.get('lead_domain') else detail['lead_company']
                delivery_display = f"{detail['delivery_company']} ({detail['delivery_domain']})" if detail.get('delivery_domain') else detail['delivery_company']
                
                simplified_details.append({
                    'Row': detail['row'],
                    'Phone': detail['phone'],
                    'Lead Company': lead_display,
                    'Delivery Company': delivery_display,
                    'Conflict': detail['conflict_message']
                })
        
        return pd.DataFrame(simplified_details)
    
    def _display_company_analysis(self, stats: Dict, is_first_delivery: bool):
        """Display company analysis for CPC"""
        if not is_first_delivery and stats.get('domain_analysis'):
            domain_analysis = stats['domain_analysis']
            with st.expander("🏢 Company & Domain Analysis (External)", expanded=False):
                st.markdown("**📊 Summary:**")
                st.write(f"• **{domain_analysis['total_domains']}** unique domains processed")
                st.write(f"• **{domain_analysis['total_companies']}** unique company names processed")
        
        if stats.get('internal_companies_checked'):
            companies_count = len(stats['internal_companies_checked'])
            with st.expander(f"🏢 Company Analysis (Internal - {companies_count} unique companies)", expanded=False):
                st.write("Companies processed during internal CPC check")
                internal_companies_list = sorted(list(stats['internal_companies_checked']))[:20]
                for company in internal_companies_list:
                    st.write(f"• {company.title()}")
                
                if companies_count > 20:
                    st.write(f"... and {companies_count - 20} more companies")
    
    def _display_duplicate_analysis(self, stats: Dict, is_first_delivery: bool):
        """Display duplicate analysis"""
        # External duplicates
        if not is_first_delivery and stats.get('duplicate_details'):
            with st.expander(f"📋 External Duplicate Details ({len(stats['duplicate_details'])} found)", expanded=False):
                df_dups = pd.DataFrame(stats['duplicate_details'])
                st.dataframe(df_dups.head(50), use_container_width=True, hide_index=True)
                
                if len(stats['duplicate_details']) > 50:
                    st.info(f"Showing first 50 duplicates out of {len(stats['duplicate_details'])} total")
        
        # Internal duplicates
        if stats.get('internal_duplicate_details'):
            with st.expander(f"📋 Internal Duplicate Details ({len(stats['internal_duplicate_details'])} found)", expanded=False):
                df_internal_dups = pd.DataFrame(stats['internal_duplicate_details'])
                st.dataframe(df_internal_dups.head(50), use_container_width=True, hide_index=True)
                
                if len(stats['internal_duplicate_details']) > 50:
                    st.info(f"Showing first 50 duplicates out of {len(stats['internal_duplicate_details'])} total")
    
    def _display_download_section(self, output_file_path: str, summary_file_path: str):
        """Display download section with enhanced options"""
        st.markdown("### 📥 Download Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with open(output_file_path, "rb") as f:
                st.download_button(
                    label="📥 Download Checked File",
                    data=f.read(),
                    file_name=f"checked_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help="Download the processed Excel file with validation results"
                )
        
        with col2:
            with open(summary_file_path, "r") as f:
                st.download_button(
                    label="📄 Download Summary Report",
                    data=f.read(),
                    file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    help="Download the detailed summary report"
                )
        
        with col3:
            if st.button("🗑️ Clean Up Files", use_container_width=True, 
                        help="Remove temporary files from server"):
                if self.cleanup_temp_files():
                    st.success("Temporary files cleaned up!")
                    st.rerun()
                else:
                    st.info("No temporary files to clean up")
    
    def _add_to_history(self, stats: Dict, is_first_delivery: bool):
        """Add processing result to history"""
        history_entry = {
            'timestamp': datetime.now(),
            'mode': 'Internal' if is_first_delivery else 'Full',
            'total_leads': stats['total_leads'],
            'passed': stats['passed'],
            'processing_time': stats['processing_time']
        }
        
        st.session_state.processing_history.append(history_entry)
        
        # Keep only last 10 entries
        if len(st.session_state.processing_history) > 10:
            st.session_state.processing_history = st.session_state.processing_history[-10:]

    def run(self):
        """Main application runner"""
        # Page config
        st.set_page_config(
            page_title="CPC & Duplicate Checker",
            page_icon="📊",
            layout="wide"
        )
        
        # Hero Section
        UIComponents.render_hero_section()
        
        # Delivery Type Selection
        is_first_delivery = UIComponents.render_delivery_type_selection()
        
        st.divider()
        
        # File Upload Section
        delivery_info, lead_info = UIComponents.render_file_upload_section(
            st.session_state, is_first_delivery
        )
        
        st.divider()
        
        # Main Processing Section
        files_ready = self._check_files_ready(is_first_delivery)
        
        if files_ready:
            self._render_processing_section(is_first_delivery)
        else:
            self._show_file_upload_info(is_first_delivery)
        
        # Footer
        self._render_footer()
    
    def _check_files_ready(self, is_first_delivery: bool) -> bool:
        """Check if required files are uploaded"""
        if is_first_delivery:
            return bool(st.session_state.lead_file)
        else:
            return bool(st.session_state.delivery_file and st.session_state.lead_file)
    
    def _render_processing_section(self, is_first_delivery: bool):
        """Render the main processing section"""
        # Get file headers with error handling
        try:
            if is_first_delivery:
                lead_headers, l_rows, l_cols = FileHandler.get_headers_from_upload(st.session_state.lead_file)
                delivery_headers = []
                st.info(f"📊 Lead file: {l_rows:,} rows × {l_cols} columns")
            else:
                delivery_headers, d_rows, d_cols = FileHandler.get_headers_from_upload(st.session_state.delivery_file)
                lead_headers, l_rows, l_cols = FileHandler.get_headers_from_upload(st.session_state.lead_file)
                st.info(f"📊 Delivery: {d_rows:,} rows × {d_cols} cols | Lead: {l_rows:,} rows × {l_cols} cols")
        except Exception as e:
            st.error(f"Error reading file headers: {e}")
            return
        
        # Select checks
        check_cpc, check_duplicates, check_phone, cpc_limit = UIComponents.render_checks_selection()
        if cpc_limit:
            st.session_state.cpc_limit = cpc_limit
        
        st.divider()
        
        # Column mapping
        mapping = UIComponents.render_column_mapping(
            delivery_headers, lead_headers, check_cpc, check_duplicates, 
            check_phone, is_first_delivery
        )
        
        st.divider()
        
        # Validation
        checks = {
            'check_cpc': check_cpc,
            'check_duplicates': check_duplicates,
            'check_phone': check_phone
        }
        
        validation_errors = get_validation_errors(mapping, checks, is_first_delivery)
        
        # Display validation errors
        for error in validation_errors:
            st.warning(f"⚠️ {error}")
        
        # Run Checks Button
        self._render_run_button(checks, mapping, is_first_delivery, 
                               button_disabled=len(validation_errors) > 0)
    
    def _render_run_button(self, checks: Dict, mapping: Dict, is_first_delivery: bool, 
                          button_disabled: bool):
        """Render the run checks button and handle processing"""
        mode_button_text = "🚀 Run Internal Validation" if is_first_delivery else "🚀 Run Full Validation"
        
        if st.button(mode_button_text, type="primary", use_container_width=True, 
                    disabled=button_disabled):
            
            with loading_spinner("Processing files and running validation checks..."):
                try:
                    # Initialize processor
                    processor = DataProcessor()
                    
                    # Process files based on mode
                    if is_first_delivery:
                        result_wb, stats = processor.process_files_internal(
                            st.session_state.lead_file,
                            mapping,
                            checks,
                            st.session_state.cpc_limit
                        )
                    else:
                        result_wb, stats = processor.process_files(
                            st.session_state.delivery_file,
                            st.session_state.lead_file,
                            mapping,
                            checks,
                            st.session_state.cpc_limit
                        )
                    
                    # Get comprehensive stats
                    comprehensive_stats = processor.get_comprehensive_stats()
                    
                    # Save output file
                    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                    result_wb.save(output_file.name)
                    result_wb.close()
                    
                    # Generate summary report
                    summary_content = self.generate_summary_report(
                        comprehensive_stats, checks, is_first_delivery
                    )
                    summary_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w')
                    summary_file.write(summary_content)
                    summary_file.close()
                    
                    # Store file paths in session state for cleanup
                    st.session_state.temp_output_file = output_file.name
                    st.session_state.temp_summary_file = summary_file.name
                    
                    # Display results
                    self.display_results(comprehensive_stats, checks, output_file.name, 
                                       summary_file.name, is_first_delivery)
                    
                except Exception as e:
                    logger.error(f"Error processing files: {e}")
                    st.error(f"❌ Error processing files: {str(e)}")
                    st.exception(e)
    
    def _show_file_upload_info(self, is_first_delivery: bool):
        """Show file upload information"""
        if is_first_delivery:
            st.info("👆 Please upload your lead file to proceed with internal validation")
        else:
            st.info("👆 Please upload both delivery file and lead file to proceed with full validation")
    
    def _render_footer(self):
        """Render application footer"""
        st.divider()
        st.markdown("""
        <hr style="margin-top: 3rem; margin-bottom: 1rem;">
        <div style='text-align: center; font-size: 14px; color: #6c757d;'>
            © 2025 Interlink. All rights reserved.<br>
            Engineered for enterprise-grade data integrity by Felix Markas Salve.
        </div>
        """, unsafe_allow_html=True)


# Main application entry point
def main():
    """Main application entry point"""
    checker = CPCDuplicateChecker()
    checker.run()


if __name__ == "__main__":
    main()