#!/usr/bin/env python3
"""
Cleanup script for web-crawler project
Removes logs, temporary files, and other artifacts before running the application.
"""

import os
import shutil
import argparse
from pathlib import Path
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Clean up temporary files before running the web crawler")
    parser.add_argument("--preserve-cookies", action="store_true", help="Preserve Facebook and other cookie files")
    parser.add_argument("--preserve-user-data", action="store_true", help="Preserve browser user data directories")
    parser.add_argument("--preserve-html", action="store_true", help="Preserve HTML debug files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    return parser.parse_args()

def cleanup(args):
    # Ensure we're in the project root directory
    if not Path("main.py").exists():
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    screenshots_dir = logs_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    # Files to always clean
    log_files = [
        logs_dir / "crawler.log",
        logs_dir / "errors.log",
        logs_dir / "startup_errors.log"
    ]
    
    # Files to clean conditionally
    html_files = [] if args.preserve_html else [
        logs_dir / "newegg_debug.html"
    ]
    
    cookie_files = [] if args.preserve_cookies else [
        logs_dir / "fb_cookies.json"
    ]
    
    # Directories to clean conditionally
    user_data_dirs = [] if args.preserve_user_data else [
        logs_dir / "fb_user_data"
    ]
    
    # Delete log files
    for log_file in log_files:
        if log_file.exists():
            if args.dry_run:
                print(f"Would delete file: {log_file}")
            else:
                print(f"Deleting file: {log_file}")
                log_file.unlink()
    
    # Delete HTML files if not preserved
    for html_file in html_files:
        if html_file.exists():
            if args.dry_run:
                print(f"Would delete file: {html_file}")
            else:
                print(f"Deleting file: {html_file}")
                html_file.unlink()
    
    # Delete cookie files if not preserved
    for cookie_file in cookie_files:
        if cookie_file.exists():
            if args.dry_run:
                print(f"Would delete file: {cookie_file}")
            else:
                print(f"Deleting file: {cookie_file}")
                cookie_file.unlink()
    
    # Clean screenshots directory
    screenshot_count = 0
    if screenshots_dir.exists():
        for screenshot in screenshots_dir.glob("*.png"):
            screenshot_count += 1
            if args.dry_run:
                print(f"Would delete screenshot: {screenshot}")
            else:
                screenshot.unlink()
        
        if screenshot_count > 0 and not args.dry_run:
            print(f"Deleted {screenshot_count} screenshots")
    
    # Clean user data directories if not preserved
    for user_data_dir in user_data_dirs:
        if user_data_dir.exists():
            if args.dry_run:
                print(f"Would delete directory: {user_data_dir}")
            else:
                print(f"Deleting directory: {user_data_dir}")
                shutil.rmtree(user_data_dir)
    
    print("Cleanup complete!")
    if args.dry_run:
        print("Note: This was a dry run. No files were actually deleted.")

if __name__ == "__main__":
    args = parse_args()
    cleanup(args) 