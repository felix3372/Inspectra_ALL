"""
Custom exceptions for Analytics Dashboard Helper package.
"""


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class FileProcessingError(Exception):
    """Custom exception for file processing errors."""
    pass


class SheetNotFoundError(Exception):
    """Custom exception when required sheets are not found."""
    pass


class AnalyticsGenerationError(Exception):
    """Custom exception for analytics generation errors."""
    pass


class ChartGenerationError(Exception):
    """Custom exception for chart generation errors."""
    pass


class PDFExportError(Exception):
    """Custom exception for PDF export errors."""
    pass