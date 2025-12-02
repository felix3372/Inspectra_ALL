"""
Inspectra QA Automation - Tools Overview
A comprehensive overview of all available QA automation tools and capabilities.
"""

import streamlit as st
from datetime import datetime

def main():
    """Main function for the Overview page."""
    st.set_page_config(
        page_title="Inspectra QA Tools Overview",
        page_icon="🔧",
        layout="wide"
    )
    
    # Custom CSS styling
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
        .tool-card {
            background: linear-gradient(145deg, #f8fbff, #ffffff);
            border-radius: 15px;
            padding: 1.8rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,123,255,0.08);
            border-left: 5px solid #00c3ff;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .tool-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,123,255,0.15);
        }
        .tool-card::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100px;
            background: linear-gradient(45deg, transparent, rgba(0,195,255,0.05));
            border-radius: 0 15px 0 100px;
        }
        .tool-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .tool-description {
            color: #4b5563;
            font-size: 1rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        .feature-list {
            list-style: none;
            padding: 0;
            margin: 1rem 0;
        }
        .feature-list li {
            padding: 0.3rem 0;
            color: #059669;
            font-weight: 500;
        }
        .feature-list li::before {
            content: "✅ ";
            margin-right: 0.5rem;
        }
        .status-badge {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 1rem;
        }
        .status-available {
            background: #d1fae5;
            color: #065f46;
        }
        .status-development {
            background: #fef3c7;
            color: #92400e;
        }
        .status-planned {
            background: #e0e7ff;
            color: #3730a3;
        }
        .stats-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 1.2rem;
            margin: 1.5rem 0;
            color: white;
            text-align: center;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        .stat-item {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 1rem;
            backdrop-filter: blur(10px);
        }
        .stat-number {
            font-size: 2rem;
            font-weight: 900;
            display: block;
        }
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 0.2rem;
        }
        .roadmap-section {
            background: #f9fafb;
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem 0;
        }
        .roadmap-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        .timeline-item {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            padding: 1rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .timeline-quarter {
            background: #3b82f6;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            min-width: 80px;
            text-align: center;
            margin-right: 1rem;
        }
        .timeline-content {
            flex: 1;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="inspectra-hero">
        <div class="inspectra-inline">
            <span class="inspectra-title">Inspectra</span>
            <span class="inspectra-divider">|</span>
            <span class="inspectra-tagline">QA Automation Platform</span>
        </div>
    </div>
    <div class="section">
        <div class="section-title">🔧 What is this?</div>
        <b>Inspectra QA Automation Platform</b> is a comprehensive suite of tools for quality assurance automation.<br>
        Streamline your QA processes with intelligent data validation, professional reporting, and interactive analytics.
    </div>
    """, unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; color: #4b5563; font-size: 1.1rem;">
        Streamline your QA processes with our suite of intelligent automation tools designed for 
        modern data-driven quality assurance workflows.
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Section (updated Active Tools: 7)
    st.markdown("""
    <div class="stats-container">
        <h2 style="margin: 0 0 1rem 0; font-size: 1.8rem;">Platform Statistics</h2>
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-number">7</span>
                <div class="stat-label">Active Tools</div>
            </div>
            <div class="stat-item">
                <span class="stat-number">100%</span>
                <div class="stat-label">Automation Rate</div>
            </div>
            <div class="stat-item">
                <span class="stat-number">50MB</span>
                <div class="stat-label">Max File Size</div>
            </div>
            <div class="stat-item">
                <span class="stat-number">48</span>
                <div class="stat-label">Max Columns</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Available Tools
    st.markdown("## 🛠️ Available Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # QA Report Generator
        st.markdown("""
        <div class="tool-card">
            <div class="tool-title">📊 QA Report Generator</div>
            <div class="tool-description">
                Advanced lead data analysis tool that processes Excel files and generates comprehensive 
                QA reports with professional formatting and email-ready output.
            </div>
            <ul class="feature-list">
                <li>Excel file processing (.xlsx, .xlsm)</li>
                <li>Data validation & cleaning</li>
                <li>Agent performance analysis</li>
                <li>DQ reason breakdown</li>
                <li>Segment-wise reporting</li>
                <li>JT Persona analysis</li>
                <li>Professional Excel export</li>
                <li>Email template generation</li>
            </ul>
            <div class="status-badge status-available">✅ Available</div>
        </div>
        """, unsafe_allow_html=True)

        # 📎 NEW: MD5 Hash Generator
        st.markdown("""
        <div class="tool-card">
            <div class="tool-title">🔐 MD5 Hash Generator</div>
            <div class="tool-description">
                Generate MD5 hashes for strings or files for quick checksum creation and integrity checks. 
                Includes single and batch modes with export.
            </div>
            <ul class="feature-list">
                <li>Instant string hashing</li>
                <li>File upload hashing</li>
                <li>Copy-to-clipboard output</li>
                <li>Batch mode (CSV/Excel column)</li>
            </ul>
            <div class="status-badge status-available">✅ Available</div>
        </div>
        """, unsafe_allow_html=True)
        
        # QA Analytics Dashboard
        st.markdown("""
        <div class="tool-card">
            <div class="tool-title">📈 QA Analytics Dashboard</div>
            <div class="tool-description">
                Interactive analytics dashboard with real-time visualizations for campaign data analysis. 
                Supports both file upload and network drive access with multiple chart types.
            </div>
            <ul class="feature-list">
                <li>Interactive Plotly visualizations</li>
                <li>Lead count analysis by sheets</li>
                <li>Country-wise distribution</li>
                <li>Disqualification reason tracking</li>
                <li>Summary dashboard overview</li>
                <li>Network drive integration</li>
                <li>File upload support</li>
                <li>Configurable column mapping</li>
            </ul>
            <div class="status-badge status-available">✅ Available</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Data Validator
        st.markdown("""
        <div class="tool-card">
            <div class="tool-title">🔍 Advanced Data Validator</div>
            <div class="tool-description">
                Intelligent validation engine with case-sensitive matching, custom rules, 
                and comprehensive error reporting for maintaining data quality standards.
            </div>
            <ul class="feature-list">
                <li>Case-sensitive DQ reason validation</li>
                <li>Lead status verification</li>
                <li>Column presence checking</li>
                <li>Custom validation rules</li>
                <li>Detailed error messages</li>
                <li>Batch processing support</li>
            </ul>
            <div class="status-badge status-available">✅ Available</div>
        </div>
        """, unsafe_allow_html=True)

        # 📎 NEW: Revenue Converter
        st.markdown("""
        <div class="tool-card">
            <div class="tool-title">💰 Revenue Converter</div>
            <div class="tool-description">
                Normalize revenue strings into clean integers (e.g., “₹1.2 Cr”, “$3.5M”, “12,34,567”) with 
                currency and suffix parsing, ready for analytics.
            </div>
            <ul class="feature-list">
                <li>Currency symbol detection</li>
                <li>K/M/B/Cr/Lakh parsing</li>
                <li>Locale-aware comma handling</li>
                <li>Bulk processing + export</li>
            </ul>
            <div class="status-badge status-available">✅ Available</div>
        </div>
        """, unsafe_allow_html=True)

        # 📎 NEW: Phone Number Validator
        st.markdown("""
        <div class="tool-card">
            <div class="tool-title">📞 Phone Number Validator</div>
            <div class="tool-description">
                Validate and format phone numbers using python-phonenumbers; supports single and bulk validation,
                with country, carrier, type and formatting outputs.
            </div>
            <ul class="feature-list">
                <li>E.164 / International / National formats</li>
                <li>Country, carrier, type, time zones</li>
                <li>Possible vs Valid with reason</li>
                <li>CSV/Excel upload + JSON/CSV export</li>
            </ul>
            <div class="status-badge status-available">✅ Available</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Future Tools
        st.markdown("""
        <div class="tool-card">
            <div class="tool-title">🚀 Upcoming Tools</div>
            <div class="tool-description">
                Next-generation QA automation tools currently in development to further 
                enhance your quality assurance workflows.
            </div>
            <ul class="feature-list">
                <li>Real-time data monitoring</li>
                <li>ML-powered anomaly detection</li>
                <li>API integration toolkit</li>
                <li>Advanced analytics dashboard</li>
                <li>Automated alert system</li>
                <li>Custom workflow builder</li>
            </ul>
            <div class="status-badge status-development">🔄 In Development</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Bottom branding
    st.markdown("""
    <hr style="margin-top: 3rem; margin-bottom: 1rem;">
    <div style='text-align: center; font-size: 14px; color: #6c757d;'>
        2025 Interlink. All rights reserved. <br>
        Built by Felix Markas Salve as an internal innovation project.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
