"""
File selector module for hierarchical network path file selection.
Allows users to navigate Month → Campaign → Excel File structure.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from Analytics_Helper import Config   # ← FIXED import (use Config)

logger = logging.getLogger(__name__)


class FileSelector:
    """Handles hierarchical file selection from network paths (Month → Campaign → File)."""

    # Default base directory comes from Config
    BASE_DIR = Config.BASE_DIR        # ← FIXED (class variable)

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize FileSelector with base directory.
        
        Args:
            base_dir: Base directory path. If None, uses BASE_DIR
        """
        self.base_dir = base_dir or self.BASE_DIR
        self.supported_extensions = ['.xlsx', '.xlsm']

    def path_exists(self, path: str = None) -> bool:
        """Check if path exists and is accessible."""
        check_path = path or self.base_dir
        try:
            return os.path.exists(check_path) and os.path.isdir(check_path)
        except Exception as e:
            logger.error(f"Error checking path: {str(e)}")
            return False

    def get_month_folders(self) -> List[str]:
        """Get list of month folders in base directory."""
        months = []

        if not self.path_exists():
            logger.warning(f"Base directory not accessible: {self.base_dir}")
            return months

        try:
            for item in os.listdir(self.base_dir):
                item_path = os.path.join(self.base_dir, item)
                if os.path.isdir(item_path):
                    months.append(item)

            months.sort()
            logger.info(f"Found {len(months)} month folders")
            return months

        except Exception as e:
            logger.error(f"Error reading month folders: {str(e)}")
            return []

    def get_campaign_folders(self, month: str) -> List[str]:
        """Get campaign folders inside a selected month."""
        campaigns = []
        month_path = os.path.join(self.base_dir, month)

        if not self.path_exists(month_path):
            logger.warning(f"Month folder not accessible: {month_path}")
            return campaigns

        try:
            for item in os.listdir(month_path):
                item_path = os.path.join(month_path, item)
                if os.path.isdir(item_path):
                    campaigns.append(item)

            campaigns.sort()
            logger.info(f"Found {len(campaigns)} campaign folders in {month}")
            return campaigns

        except Exception as e:
            logger.error(f"Error reading campaign folders: {str(e)}")
            return []

    def get_excel_files(self, month: str, campaign: str) -> List[Tuple[str, str, datetime, float]]:
        """Get Excel files inside a campaign folder."""
        files = []
        campaign_path = os.path.join(self.base_dir, month, campaign)

        if not self.path_exists(campaign_path):
            logger.warning(f"Campaign folder not accessible: {campaign_path}")
            return files

        try:
            for file in os.listdir(campaign_path):
                file_path = os.path.join(campaign_path, file)

                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file)
                    if ext.lower() in self.supported_extensions:
                        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        size_mb = os.path.getsize(file_path) / (1024 * 1024)
                        files.append((file, file_path, mod_time, size_mb))

            files.sort(key=lambda x: x[2], reverse=True)
            logger.info(f"Found {len(files)} Excel files in {campaign}")
            return files

        except Exception as e:
            logger.error(f"Error reading Excel files: {str(e)}")
            return []

    def get_file_display_name(self, filename: str, mod_time: datetime, size_mb: float) -> str:
        """Return formatted display name for UI."""
        return f"{filename} ({size_mb:.1f} MB, {mod_time.strftime('%d-%b-%Y %I:%M %p')})"

    def read_file(self, file_path: str) -> Optional[bytes]:
        """Read file contents from network share."""
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return None

    def validate_file_access(self, file_path: str) -> Tuple[bool, str]:
        """Validate file exists and is readable."""
        if not os.path.exists(file_path):
            return False, "File does not exist"

        if not os.path.isfile(file_path):
            return False, "Path is not a file"

        try:
            with open(file_path, 'rb') as f:
                f.read(1)
            return True, "File is accessible"
        except PermissionError:
            return False, "Permission denied"
        except Exception as e:
            return False, f"Error accessing file: {str(e)}"

    def get_full_path(self, month: str, campaign: str, filename: str) -> str:
        """Construct absolute path for a file."""
        return os.path.join(self.base_dir, month, campaign, filename)