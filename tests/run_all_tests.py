#!/usr/bin/env python3
"""
Main test runner for all test suites
"""

import subprocess
import sys
import os

def run_test_suite(suite_path, description):
    """Run a test suite and report results"""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            ["uv", "run", "python", os.path.join(suite_path, "run_tests.py")],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        if result.returncode == 0:
            print(f"✅ {description} PASSED")
            print(result.stdout)
            return True
        else:
            print(f"❌ {description} FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ {description} ERROR: {e}")
        return False

def main():
    """Run all test suites"""
    print("🚀 Running all test suites...")
    
    test_suites = [
        ("tests/BatchJobStatesTests", "Batch Job States Tests")
        # Add more test suites here as they are created
        # ("tests/OtherStateMachineTests", "Other State Machine Tests")
    ]
    
    passed = 0
    total = len(test_suites)
    
    for suite_path, description in test_suites:
        if run_test_suite(suite_path, description):
            passed += 1
    
    print(f"\n{'='*60}")
    print(f"OVERALL TEST SUMMARY: {passed}/{total} test suites passed")
    print(f"{'='*60}")
    
    if passed == total:
        print("🎉 All test suites passed!")
        return 0
    else:
        print("❌ Some test suites failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())