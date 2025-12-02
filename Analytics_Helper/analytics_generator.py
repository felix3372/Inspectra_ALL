"""
Analytics generation logic for Analytics Dashboard Helper package.
Generates various analytics reports and statistics from processed data.
"""

from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import logging

from .data_processor import DataProcessor

logger = logging.getLogger(__name__)


class AnalyticsGenerator:
    """Generates various analytics reports from processed data."""
    
    @staticmethod
    def generate_sheet_wise_count(sheet_counts: Dict[str, int]) -> List[List[Any]]:
        """
        Generate sheet-wise data count report.
        
        Args:
            sheet_counts: Dictionary mapping sheet names to record counts
            
        Returns:
            List of lists for table display [headers, ...rows]
        """
        report = [["Sheet Name", "Record Count"]]
        
        # Add each sheet with its count
        for sheet_name, count in sheet_counts.items():
            report.append([sheet_name, count])
        
        # Add total
        total_records = sum(sheet_counts.values())
        report.append(["Total Records", total_records])
        
        logger.info(f"Generated sheet-wise count for {len(sheet_counts)} sheets")
        return report
    
    @staticmethod
    def generate_segment_wise_analysis(records: List[Dict[str, Any]]) -> List[List[Any]]:
        """
        Generate segment-wise qualified and disqualified count.
        
        Args:
            records: Combined list of qualified and disqualified records
            
        Returns:
            List of lists for table display
        """
        segment_data = defaultdict(lambda: {"Qualified": 0, "Disqualified": 0})
        
        for record in records:
            segment = record.get("Segment Tagging")
            if segment is None or str(segment).strip() == "":
                segment = "(Blank)"
            else:
                segment = str(segment).strip()
            
            status = DataProcessor.normalize(record.get("Lead Status", ""))
            
            if status == "qualified":
                segment_data[segment]["Qualified"] += 1
            elif status == "disqualified":
                segment_data[segment]["Disqualified"] += 1
        
        # Sort by total count descending
        segment_rows = []
        for segment, counts in segment_data.items():
            total = counts["Qualified"] + counts["Disqualified"]
            segment_rows.append([segment, counts["Qualified"], counts["Disqualified"], total])
        
        segment_rows.sort(key=lambda x: x[3], reverse=True)
        
        # Add grand total
        if segment_rows:
            total_qualified = sum(row[1] for row in segment_rows)
            total_disqualified = sum(row[2] for row in segment_rows)
            grand_total = total_qualified + total_disqualified
            segment_rows.append(["Grand Total", total_qualified, total_disqualified, grand_total])
        
        # Create report with headers
        report = [["Segment", "Qualified", "Disqualified", "Total"]]
        report.extend(segment_rows)
        
        logger.info(f"Generated segment-wise analysis for {len(segment_rows)-1} segments")
        return report
    
    @staticmethod
    def generate_dq_reason_analytics(records: List[Dict[str, Any]]) -> Tuple[List[List[Any]], Dict[str, int]]:
        """
        Generate DQ reason analytics.
        
        Args:
            records: Combined list of records
            
        Returns:
            Tuple of (table_data, reason_counts_dict for chart)
        """
        reason_counts = Counter()
        total_disqualified = 0
        
        for record in records:
            status = DataProcessor.normalize(record.get("Lead Status", ""))
            if status == "disqualified":
                reason = record.get("DQ Reason") or "(Blank)"
                reason_counts[reason] += 1
                total_disqualified += 1
        
        # Sort by count descending
        reason_rows = []
        for reason, count in reason_counts.most_common():
            percentage = (count / total_disqualified * 100) if total_disqualified > 0 else 0
            reason_rows.append([reason, count, f"{percentage:.1f}%"])
        
        # Add total
        if reason_rows:
            reason_rows.append(["Total", total_disqualified, "100.0%"])
        
        # Create report
        report = [["DQ Reason", "Count", "Percentage"]]
        report.extend(reason_rows)
        
        logger.info(f"Generated DQ reason analytics for {len(reason_counts)} unique reasons")
        return report, dict(reason_counts)
    
    @staticmethod
    def generate_qualified_disqualified_summary(records: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Generate qualified vs disqualified summary counts.
        
        Args:
            records: Combined list of records
            
        Returns:
            Dictionary with counts
        """
        qualified_count = 0
        disqualified_count = 0
        
        for record in records:
            status = DataProcessor.normalize(record.get("Lead Status", ""))
            if status == "qualified":
                qualified_count += 1
            elif status == "disqualified":
                disqualified_count += 1
        
        return {
            "Qualified": qualified_count,
            "Disqualified": disqualified_count
        }
    
    @staticmethod
    def generate_email_status_qualified_count(records: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Generate email status wise qualified count.
        
        Args:
            records: Combined list of records
            
        Returns:
            Dictionary mapping email status to qualified count
        """
        return AnalyticsGenerator.generate_email_status_qualified_count_dynamic(records, "Email Status 1")
    
    @staticmethod
    def generate_email_status_qualified_count_dynamic(records: List[Dict[str, Any]], column_name: str) -> Dict[str, int]:
        """
        Generate email status wise qualified count for any column.
        
        Args:
            records: Combined list of records
            column_name: Name of the email status column
            
        Returns:
            Dictionary mapping email status to qualified count
        """
        email_status_counts = Counter()
        
        for record in records:
            status = DataProcessor.normalize(record.get("Lead Status", ""))
            if status == "qualified":
                email_status = record.get(column_name)
                if email_status is None or str(email_status).strip() == "":
                    email_status = "(Blank)"
                else:
                    email_status = str(email_status).strip()
                
                email_status_counts[email_status] += 1
        
        logger.info(f"Generated email status analytics for {len(email_status_counts)} statuses using column '{column_name}'")
        return dict(email_status_counts)
    
    @staticmethod
    def generate_custom_column_qualified_count(records: List[Dict[str, Any]], column_name: str) -> List[List[Any]]:
        """
        Generate qualified and disqualified count for any custom column.
        Shows breakdown by Qualified/Disqualified status.
        """
        from collections import defaultdict
        
        column_data = defaultdict(lambda: {"Qualified": 0, "Disqualified": 0})
        
        for record in records:
            status = DataProcessor.normalize(record.get("Lead Status", ""))
            value = record.get(column_name)
            
            # Normalize value
            if not value or str(value).strip() == "":
                value = "(Blank)"
            else:
                value = str(value).strip()
            
            if status == "qualified":
                column_data[value]["Qualified"] += 1
            elif status == "disqualified":
                column_data[value]["Disqualified"] += 1
        
        # Sort by total count descending
        column_rows = []
        for value, counts in column_data.items():
            total = counts["Qualified"] + counts["Disqualified"]
            column_rows.append([value, counts["Qualified"], counts["Disqualified"], total])
        
        column_rows.sort(key=lambda x: x[3], reverse=True)
        
        # Add total
        if column_rows:
            total_qualified = sum(row[1] for row in column_rows)
            total_disqualified = sum(row[2] for row in column_rows)
            grand_total = total_qualified + total_disqualified
            column_rows.append(["Total", total_qualified, total_disqualified, grand_total])
        
        # Build final report
        report = [[column_name, "Qualified", "Disqualified", "Total"]]
        report.extend(column_rows)
        
        return report
    
    @staticmethod
    def generate_sheet_wise_custom_report(sheet_df, column_name: str) -> List[List[Any]]:
        """
        Generate count report for any column in any sheet.
        Just counts occurrences of each value.
        
        Args:
            sheet_df: Pandas DataFrame of the selected sheet
            column_name: Column name to analyze
            
        Returns:
            List of lists for table display
        """
        if column_name not in sheet_df.columns:
            return [[column_name, "Count"], ["Column not found", 0]]
        
        column_counts = Counter()
        
        for value in sheet_df[column_name]:
            # Normalize value
            if value is None or str(value).strip() == "":
                normalized_value = "(Blank)"
            else:
                normalized_value = str(value).strip()
            
            column_counts[normalized_value] += 1
        
        # Sort by count descending
        column_rows = [[value, count] for value, count in column_counts.most_common()]
        
        # Add total
        if column_rows:
            total = sum(row[1] for row in column_rows)
            column_rows.append(["Total", total])
        
        # Build final report
        report = [[column_name, "Count"]]
        report.extend(column_rows)
        
        return report

    
    @staticmethod
    def generate_summary_statistics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate overall summary statistics.
        
        Args:
            records: Combined list of records
            
        Returns:
            Dictionary with summary statistics
        """
        total_records = len(records)
        qualified_count = sum(1 for r in records if DataProcessor.normalize(r.get("Lead Status", "")) == "qualified")
        disqualified_count = sum(1 for r in records if DataProcessor.normalize(r.get("Lead Status", "")) == "disqualified")
        
        qualified_rate = (qualified_count / total_records * 100) if total_records > 0 else 0
        disqualified_rate = (disqualified_count / total_records * 100) if total_records > 0 else 0
        
        return {
            "total_records": total_records,
            "qualified_count": qualified_count,
            "disqualified_count": disqualified_count,
            "qualified_rate": qualified_rate,
            "disqualified_rate": disqualified_rate
        }