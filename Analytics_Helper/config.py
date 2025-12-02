"""
Configuration classes for Analytics Dashboard Helper package.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Config:
    """Configuration constants for the Analytics Dashboard application."""

    BASE_DIR = r"W:\\2025" # Shared drive root path for Dashboard


    # Required sheets in Excel file
    REQUIRED_SHEETS: Tuple[str, ...] = ("Qualified", "Disqualified")
    
    # Required columns in Qualified/Disqualified sheets
    REQUIRED_COLUMNS: Tuple[str, ...] = ("Lead Status", "Audit Date")
    
    # Optional columns for analytics
    OPTIONAL_COLUMNS: Tuple[str, ...] = ("Segment Tagging", "Email Status 1", "DQ Reason")
    
    # Accepted Lead Status values
    ACCEPTED_LEAD_STATUS: Tuple[str, ...] = ("Qualified", "Disqualified")
    
    # File upload constraints
    MAX_FILE_SIZE_MB: int = 100
    SUPPORTED_EXTENSIONS: Tuple[str, ...] = ('xlsx', 'xlsm')
    
    # Chart color schemes
    QUALIFIED_COLOR: str = "#28a745"  # Green
    DISQUALIFIED_COLOR: str = "#dc3545"  # Red
    CHART_COLORS: Tuple[str, ...] = (
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
    )
    
    # PDF Export settings
    PDF_TITLE: str = "Inspectra Analytics"
    PDF_PAGE_SIZE: str = "A4"
    

@dataclass(frozen=True)
class ChartConfig:
    """Configuration for chart generation."""
    
    # Chart dimensions
    DEFAULT_WIDTH: int = 800
    DEFAULT_HEIGHT: int = 500
    DONUT_SIZE: int = 600
    
    # Chart styling
    TEMPLATE: str = "plotly_white"
    FONT_FAMILY: str = "Arial"
    TITLE_FONT_SIZE: int = 16
    LABEL_FONT_SIZE: int = 12