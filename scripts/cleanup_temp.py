"""
Temporary Cache Cleanup Utility for TalentFlow-AI.

Scans the temporary directory (default: `backend/temp/`), calculates file ages,
and deletes files older than N days (default: 7). Provides a detailed breakdown
of files removed and total disk space freed in KB/MB.

Usage:
    python scripts/cleanup_temp.py [--days 7] [--dry-run] [--temp-dir PATH]
"""

import sys
import os
import time
import argparse
import logging
from typing import List, Dict, Any, Tuple

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cleanup_temp")

# Default target directory: backend/temp
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_TEMP_DIR = os.path.join(PROJECT_ROOT, "backend", "temp")


def format_bytes(size_bytes: int) -> str:
    """Format byte size into human readable string (B, KB, MB, GB)."""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB"]
    unit_idx = 0
    size = float(size_bytes)
    while size >= 1024.0 and unit_idx < len(units) - 1:
        size /= 1024.0
        unit_idx += 1
    return f"{size:.2f} {units[unit_idx]}"


def cleanup_temp_cache(temp_dir: str, days: int, dry_run: bool = False) -> Dict[str, Any]:
    """
    Delete files in temp_dir older than `days` days.

    Args:
        temp_dir: Path to temporary directory.
        days: Threshold age in days for file deletion.
        dry_run: If True, simulate without deleting files.

    Returns:
        Dictionary summary containing total files scanned, deleted, and space freed.
    """
    logger.info(f"Scanning directory: '{temp_dir}' for files older than {days} days...")
    
    if not os.path.exists(temp_dir):
        logger.warning(f"Target directory '{temp_dir}' does not exist. Creating directory for future cache storage.")
        os.makedirs(temp_dir, exist_ok=True)
        return {"scanned_files": 0, "deleted_files": 0, "space_freed_bytes": 0}

    cutoff_seconds = time.time() - (days * 86400)
    scanned_count = 0
    deleted_count = 0
    space_freed_bytes = 0
    deleted_files_list: List[Tuple[str, int]] = []
    failed_files_list: List[str] = []

    for root, _, files in os.walk(temp_dir):
        for file_name in files:
            scanned_count += 1
            file_path = os.path.join(root, file_name)
            
            try:
                stat = os.stat(file_path)
                mtime = stat.st_mtime
                file_size = stat.st_size
                
                if mtime < cutoff_seconds:
                    if dry_run:
                        logger.info(f"[DRY RUN] Would delete: {file_path} ({format_bytes(file_size)})")
                    else:
                        os.remove(file_path)
                        logger.info(f"Deleted file: {file_path} ({format_bytes(file_size)})")
                    
                    deleted_count += 1
                    space_freed_bytes += file_size
                    deleted_files_list.append((file_path, file_size))
            except Exception as e:
                logger.error(f"Failed to process file '{file_path}': {e}")
                failed_files_list.append(file_path)

    mode_label = "[DRY RUN] " if dry_run else ""
    formatted_space = format_bytes(space_freed_bytes)
    
    print("\n" + "=" * 65)
    print(f"       TALENTFLOW-AI TEMP CACHE CLEANUP SUMMARY {mode_label}")
    print("=" * 65)
    print(f"Target Directory:    {temp_dir}")
    print(f"Age Cutoff:          {days} days")
    print(f"Files Scanned:       {scanned_count}")
    print(f"Files Deleted:       {deleted_count}")
    print(f"Total Space Freed:   {formatted_space}")
    print(f"Failed Deletions:    {len(failed_files_list)}")
    print("=" * 65 + "\n")

    return {
        "scanned_files": scanned_count,
        "deleted_files": deleted_count,
        "space_freed_bytes": space_freed_bytes,
        "space_freed_readable": formatted_space,
        "failed_files": failed_files_list
    }


def main():
    parser = argparse.ArgumentParser(description="Clean temporary cache files in TalentFlow-AI backend.")
    parser.add_argument("--days", type=int, default=7, help="Delete files older than N days (default: 7)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate cleanup without deleting files")
    parser.add_argument("--temp-dir", type=str, default=DEFAULT_TEMP_DIR, help="Path to temporary cache directory")
    
    args = parser.parse_args()
    cleanup_temp_cache(temp_dir=args.temp_dir, days=args.days, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
