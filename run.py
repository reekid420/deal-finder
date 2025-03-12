#!/home/r33k1d/dev-stuff/web-crawler/venv312/bin/python3
"""
Run script for web-crawler project
Optionally cleans up temporary files, then runs the main application.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import cleanup

def parse_args():
    parser = argparse.ArgumentParser(description="Run the web crawler with optional cleanup")
    parser.add_argument("--clean", action="store_true", help="Clean temporary files before running")
    parser.add_argument("--preserve-cookies", action="store_true", help="Preserve Facebook and other cookie files")
    parser.add_argument("--preserve-user-data", action="store_true", help="Preserve browser user data directories")
    parser.add_argument("--preserve-html", action="store_true", help="Preserve HTML debug files")
    parser.add_argument("--debug", action="store_true", help="Run with debug output")
    return parser.parse_args()

def run_application(args):
    # Ensure we're in the project root directory
    if not Path("main.py").exists():
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Perform cleanup if requested
    if args.clean:
        print("Cleaning up temporary files...")
        # Create cleanup args object with the same attributes
        cleanup_args = argparse.Namespace(
            preserve_cookies=args.preserve_cookies,
            preserve_user_data=args.preserve_user_data,
            preserve_html=args.preserve_html,
            dry_run=False
        )
        cleanup.cleanup(cleanup_args)
        print("Cleanup complete. Starting application...")
    
    # Prepare environment for the main application
    env = os.environ.copy()
    if args.debug:
        env["DEBUG"] = "1"
    
    # Run the main application
    print("=" * 80)
    print("Starting web crawler...")
    print("=" * 80)
    
    try:
        subprocess.run([sys.executable, "main.py"], env=env)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error running application: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    args = parse_args()
    sys.exit(run_application(args)) 