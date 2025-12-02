"""
Data processing logic for Analytics Dashboard Helper package.
Handles Excel file loading, sheet parsing, and data cleaning.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, date
import pandas as pd
from io import BytesIO

from .exceptions import FileProcessingError, SheetNotFoundError

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles data loading and processing from Excel files."""
    
    def __init__(self, config):
        self.config = config
        self.all_sheets = {}
        self.qualified_records = []
        self.disqualified_records = []
    
    @staticmethod
    def normalize(value: Any) -> str:
        """Normalize string values for comparison."""
        if value is None or pd.isna(value):
            return ""
        return str(value).strip().lower()
    
    @staticmethod
    def normalize_proper_case(value: Any) -> str:
        """Normalize values to Proper Case."""
        if value is None or pd.isna(value):
            return "(Blank)"
        return str(value).strip().title()
    
    def load_excel_file(self, uploaded_file) -> Tuple[List[str], Dict[str, int]]:
        """
        Load Excel file and get all sheet names with record counts.
        
        Args:
            uploaded_file: Streamlit UploadedFile object or file path
            
        Returns:
            Tuple of (sheet_names_list, sheet_counts_dict)
        """
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            
            logger.info(f"Found {len(sheet_names)} sheets in Excel file")
            
            # Count records in each sheet
            sheet_counts = {}
            for sheet_name in sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                sheet_counts[sheet_name] = len(df)
                self.all_sheets[sheet_name] = df
            
            return sheet_names, sheet_counts
            
        except Exception as e:
            logger.error(f"Error loading Excel file: {str(e)}")
            raise FileProcessingError(f"Failed to load Excel file: {str(e)}")
    
    def validate_required_sheets(self, sheet_names: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that required sheets exist in the Excel file.
        
        Args:
            sheet_names: List of sheet names from Excel file
            
        Returns:
            Tuple of (is_valid, missing_sheets_list)
        """
        missing_sheets = []
        for required_sheet in self.config.REQUIRED_SHEETS:
            if required_sheet not in sheet_names:
                missing_sheets.append(required_sheet)
        
        is_valid = len(missing_sheets) == 0
        
        if not is_valid:
            logger.warning(f"Missing required sheets: {missing_sheets}")
        
        return is_valid, missing_sheets
    
    def load_and_parse_sheets(self, uploaded_file) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Load Qualified and Disqualified sheets and parse them into records.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Tuple of (qualified_records, disqualified_records)
        """
        try:
            # Load Qualified sheet
            qualified_df = pd.read_excel(uploaded_file, sheet_name="Qualified")
            qualified_records = qualified_df.to_dict('records')
            
            # Load Disqualified sheet
            disqualified_df = pd.read_excel(uploaded_file, sheet_name="Disqualified")
            disqualified_records = disqualified_df.to_dict('records')
            
            logger.info(f"Loaded {len(qualified_records)} qualified records and {len(disqualified_records)} disqualified records")
            
            self.qualified_records = qualified_records
            self.disqualified_records = disqualified_records
            
            return qualified_records, disqualified_records
            
        except Exception as e:
            logger.error(f"Error parsing sheets: {str(e)}")
            raise SheetNotFoundError(f"Failed to parse Qualified/Disqualified sheets: {str(e)}")
    
    def get_combined_records(self) -> List[Dict[str, Any]]:
        """
        Get combined records from both Qualified and Disqualified sheets.
        
        Returns:
            Combined list of all records
        """
        return self.qualified_records + self.disqualified_records
    
    def get_column_headers(self, records: List[Dict[str, Any]]) -> List[str]:
        """
        Extract column headers from records.
        
        Args:
            records: List of data records
            
        Returns:
            List of column names
        """
        if not records:
            return []
        
        return list(records[0].keys())
    
    def check_optional_columns(self, headers: List[str]) -> Dict[str, bool]:
        """
        Check which optional columns are available in the data.
        
        Args:
            headers: List of column headers
            
        Returns:
            Dictionary mapping column names to availability status
        """
        available_columns = {}
        
        for col in self.config.OPTIONAL_COLUMNS:
            available_columns[col] = col in headers
        
        return available_columns
    
    def clean_data(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean data records by handling None values and normalizing dates + reporting fields.
        """
        cleaned_records = []
        
        REPORTING_COLUMNS = ["Lead Status", "Segment Tagging", "Email Status 1", "DQ Reason"]

        for record in records:
            cleaned_record = {}
            
            for key, value in record.items():
                
                # Handle None / NaN
                if value is None or pd.isna(value):
                    cleaned_record[key] = ""
                    continue
                
                # Handle datetime objects
                if isinstance(value, (datetime, pd.Timestamp)):
                    cleaned_record[key] = value.date()
                    continue
                
                # Normalize important reporting columns to proper case
                if key in REPORTING_COLUMNS:
                    cleaned_record[key] = self.normalize_proper_case(value)
                    continue
                
                # Default passthrough
                cleaned_record[key] = value
            
            cleaned_records.append(cleaned_record)
        
        return cleaned_records


    def filter_records_by_date(self, records: List[Dict[str, Any]], selected_date: date, date_column: str = "Audit Date") -> List[Dict[str, Any]]:
        """
        Filter records by a specific date.
        
        Args:
            records: List of data records
            selected_date: Date to filter by
            date_column: Name of the date column
            
        Returns:
            Filtered list of records
        """
        filtered_records = []
        
        for record in records:
            record_date = record.get(date_column)
            
            # Handle different date formats
            if isinstance(record_date, (datetime, pd.Timestamp)):
                record_date = record_date.date()
            elif isinstance(record_date, str):
                try:
                    record_date = pd.to_datetime(record_date).date()
                except:
                    continue
            
            if record_date == selected_date:
                filtered_records.append(record)
        
        return filtered_records
    
    def get_unique_dates(self, records: List[Dict[str, Any]], date_column: str = "Audit Date") -> List[date]:
        """
        Extract unique dates from records.
        
        Args:
            records: List of data records
            date_column: Name of the date column
            
        Returns:
            Sorted list of unique dates
        """
        unique_dates = set()
        
        for record in records:
            record_date = record.get(date_column)
            
            # Handle different date formats
            if isinstance(record_date, (datetime, pd.Timestamp)):
                unique_dates.add(record_date.date())
            elif isinstance(record_date, str):
                try:
                    parsed_date = pd.to_datetime(record_date).date()
                    unique_dates.add(parsed_date)
                except:
                    continue
            elif isinstance(record_date, date):
                unique_dates.add(record_date)
        
        return sorted(list(unique_dates))
    
    def get_available_columns_for_custom_report(self, records: List[Dict[str, Any]]) -> List[str]:
        """
        Get list of available columns suitable for custom reports (excluding system columns).
        
        Args:
            records: List of data records
            
        Returns:
            List of column names suitable for custom reports
        """
        if not records:
            return []
        
        # Get all columns
        all_columns = list(records[0].keys())
        
        # Exclude system/metadata columns
        excluded_columns = ['Lead Status', 'Audit Date', 'Agent Name', 'Lead ID', 'ID']
        
        available_columns = [col for col in all_columns if col not in excluded_columns]
        
        return sorted(available_columns)