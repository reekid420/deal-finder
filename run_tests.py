#!/usr/bin/env python
import os
import sys
import subprocess
import argparse

def run_tests(module=None, verbose=False, coverage=False):
    """Run pytest with specified options"""
    print("=" * 80)
    print("RUNNING WEB CRAWLER TESTS")
    print("=" * 80)
    
    # Ensure pytest is installed
    try:
        import pytest
    except ImportError:
        print("Installing pytest and dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
    
    # Construct command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add verbose flag if requested
    if verbose:
        cmd.append("-v")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=scrapers", "--cov=utils", "--cov-report", "term"])
    
    # Add specific module if provided
    if module:
        if not module.startswith("tests/"):
            module = f"tests/{module}"
        cmd.append(module)
    
    # Run the tests
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run web crawler tests")
    parser.add_argument("-m", "--module", help="Specific test module to run (e.g. 'scrapers/sites/test_facebook.py')")
    parser.add_argument("-v", "--verbose", action="store_true", help="Run tests with verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run tests with coverage report")
    
    args = parser.parse_args()
    
    # Create temp directory for test files if it doesn't exist
    os.makedirs("tests/temp", exist_ok=True)
    os.makedirs("tests/temp/screenshots", exist_ok=True)
    
    sys.exit(run_tests(args.module, args.verbose, args.coverage)) 