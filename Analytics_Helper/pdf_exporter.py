"""
PDF export functionality for Analytics Dashboard Helper package.
Generates professional PDF reports with charts and tables.
"""

import io
import logging
from typing import Dict, List, Any
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


class PDFExporter:
    """Handles PDF report generation with charts and tables."""
    
    def __init__(self, config):
        self.config = config
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for PDF."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
    
    def create_pdf_report(
        self,
        campaign_id: str,
        analytics_data: Dict[str, Any],
        charts: Dict[str, go.Figure]
    ) -> bytes:
        """
        Create comprehensive PDF report with all analytics.
        
        Args:
            campaign_id: Campaign identifier
            analytics_data: Dictionary containing all analytics tables
            charts: Dictionary containing Plotly figures
            
        Returns:
            PDF content as bytes
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            story = []
            
            # Add title page
            story.extend(self._create_title_page(campaign_id))
            
            # Add summary statistics
            if 'summary_stats' in analytics_data:
                story.extend(self._create_summary_section(analytics_data['summary_stats']))
            
            # Add sheet-wise count table
            if 'sheet_wise_count' in analytics_data:
                story.append(Paragraph("Sheet Wise Data Count", self.styles['SectionHeading']))
                story.append(self._create_table(analytics_data['sheet_wise_count']))
                story.append(Spacer(1, 20))
            
            # Add Qualified vs Disqualified chart
            if 'qualified_disqualified_chart' in charts:
                story.append(PageBreak())
                story.append(Paragraph("Qualified vs Disqualified Analysis", self.styles['SectionHeading']))
                story.append(self._create_chart_image(charts['qualified_disqualified_chart']))
                story.append(Spacer(1, 20))
            
            # Add Segment Wise Analysis table
            if 'segment_wise_analysis' in analytics_data:
                story.append(Paragraph("Segment Wise Analysis", self.styles['SectionHeading']))
                story.append(self._create_table(analytics_data['segment_wise_analysis']))
                story.append(Spacer(1, 20))
            
            # Add DQ Reason Analytics
            if 'dq_reason_table' in analytics_data:
                story.append(PageBreak())
                story.append(Paragraph("DQ Reason Analytics", self.styles['SectionHeading']))
                story.append(self._create_table(analytics_data['dq_reason_table']))
                story.append(Spacer(1, 20))
            
            # Add DQ Reason Chart
            if 'dq_reason_chart' in charts:
                story.append(self._create_chart_image(charts['dq_reason_chart']))
                story.append(Spacer(1, 20))
            
            # Add Email Status Donut Chart
            if 'email_status_chart' in charts:
                story.append(PageBreak())
                story.append(Paragraph("Email Status - Qualified Leads", self.styles['SectionHeading']))
                story.append(self._create_chart_image(charts['email_status_chart']))
                story.append(Spacer(1, 20))
            
            # Add Custom Column Report (if exists)
            if 'custom_column_report' in analytics_data:
                story.append(PageBreak())
                story.append(Paragraph(f"{analytics_data.get('custom_column_name', 'Custom')} Analysis", self.styles['SectionHeading']))
                story.append(self._create_table(analytics_data['custom_column_report']))
                story.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report created successfully for campaign {campaign_id}")
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating PDF report: {str(e)}")
            raise
    
    def _create_title_page(self, campaign_id: str) -> List:
        """Create title page elements."""
        elements = []
        
        # Main title
        title = Paragraph(self.config.PDF_TITLE, self.styles['CustomTitle'])
        elements.append(title)
        
        # Campaign ID
        subtitle = Paragraph(f"Campaign: {campaign_id}", self.styles['CustomSubtitle'])
        elements.append(subtitle)
        
        # Generation date
        date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        date_para = Paragraph(date_text, self.styles['Normal'])
        elements.append(Spacer(1, 10))
        elements.append(date_para)
        
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_summary_section(self, summary_stats: Dict[str, Any]) -> List:
        """Create summary statistics section."""
        elements = []
        
        elements.append(Paragraph("Summary Statistics", self.styles['SectionHeading']))
        
        summary_data = [
            ["Metric", "Value"],
            ["Total Records", f"{summary_stats['total_records']:,}"],
            ["Qualified", f"{summary_stats['qualified_count']:,} ({summary_stats['qualified_rate']:.1f}%)"],
            ["Disqualified", f"{summary_stats['disqualified_count']:,} ({summary_stats['disqualified_rate']:.1f}%)"]
        ]
        
        summary_table = self._create_table(summary_data)
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_table(self, data: List[List[Any]]) -> Table:
        """
        Create a formatted table from data.
        
        Args:
            data: List of lists (table data with headers)
            
        Returns:
            ReportLab Table object
        """
        if not data or len(data) < 1:
            return Table([["No data available"]])
        
        # Create table
        table = Table(data, repeatRows=1)
        
        # Define table style
        style = TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#BDD7EE')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body style
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            
            # Last row (Total/Grand Total) style
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#BDD7EE')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ])
        
        table.setStyle(style)
        
        return table
    
    def _create_chart_image(self, fig: go.Figure, width: float = 5.5, height: float = 4) -> Image:
        """
        Convert Plotly figure to image for PDF.
        
        Args:
            fig: Plotly figure object
            width: Width in inches
            height: Height in inches
            
        Returns:
            ReportLab Image object
        """
        try:
            # Convert plotly figure to image bytes
            img_bytes = fig.to_image(format='png', width=int(width * 150), height=int(height * 150))
            
            # Create BytesIO object
            img_buffer = io.BytesIO(img_bytes)
            
            # Create ReportLab Image
            img = Image(img_buffer, width=width * inch, height=height * inch)
            
            return img
            
        except Exception as e:
            logger.error(f"Error creating chart image: {str(e)}")
            # Return placeholder text if image creation fails
            return Paragraph("Chart could not be rendered", self.styles['Normal'])