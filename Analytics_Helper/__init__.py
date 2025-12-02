"""
Analytics Dashboard Helper Package
A modular package for analytics dashboard functionality.
"""

from .config import Config, ChartConfig
from .exceptions import (
    ValidationError,
    FileProcessingError,
    SheetNotFoundError,
    AnalyticsGenerationError,
    ChartGenerationError,
    PDFExportError
)
from .data_processor import DataProcessor
from .data_validator import DataValidator
from .analytics_generator import AnalyticsGenerator
from .chart_generator import ChartGenerator
from .pdf_exporter import PDFExporter
from .file_selector import FileSelector


__version__ = "1.0.0"
__author__ = "Felix Markas Salve"

__all__ = [
    "Config",
    "ChartConfig",
    "ValidationError",
    "FileProcessingError",
    "SheetNotFoundError",
    "AnalyticsGenerationError",
    "ChartGenerationError",
    "PDFExportError",
    "DataProcessor",
    "DataValidator",
    "AnalyticsGenerator",
    "ChartGenerator",
    "PDFExporter",
    "FileSelector"
]