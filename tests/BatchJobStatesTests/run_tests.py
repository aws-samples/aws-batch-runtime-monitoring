#!/usr/bin/env python3
"""
Test runner for all BatchJobsStates tests
"""

import subprocess
import sys
import os

def run_test(test_file, description):
    """Run a test file and report results"""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            ["uv", "run", "python", os.path.join("tests", "BatchJobStatesTests", test_file)],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    """Run all tests"""
    print("🚀 Running all BatchJobsStates tests...")
    
    tests = [
        ("test_parse_job_attributes.py", "Lambda Function Tests"),
        ("test_state_machine.py", "State Machine Simulation Tests")
    ]
    
    passed = 0
    total = len(tests)
    
    for test_file, description in tests:
        if run_test(test_file, description):
            passed += 1
    
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print(f"{'='*60}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())