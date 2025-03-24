#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAZOP Analysis Tool - Test Runner
Run all tests with coverage reporting
"""
import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """Run all tests with coverage reporting"""
    # Determine the root directory of the project
    root_dir = Path(__file__).parent.absolute()
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", 
        "pytest", 
        os.path.join(root_dir, "tests"),
        "--cov=app",
        "--cov-report=term",
        "--cov-report=html:coverage_html",
        "-v"
    ]
    
    print(f"Running tests with command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    # Return the exit code from pytest
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests()) 