#!/usr/bin/env python3
"""
Test script for ParseJobAttributesFunction Lambda function
"""

import json
import sys
import os

# Add the BatchJobsStates directory to Python path to import the function
script_dir = os.path.dirname(os.path.abspath(__file__))
batch_jobs_states_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), "src", "BatchJobsStates")
sys.path.insert(0, batch_jobs_states_dir)

from ParseJobAttributesFunction import lambda_handler


def load_test_event(filename):
    """Load a test event from the batch-job-state-change-events folder"""
    # Get the directory of this script to find the events folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    events_path = os.path.join(script_dir, "batch-job-state-change-events", filename)
    
    with open(events_path, 'r') as f:
        return json.load(f)


def test_starting_event():
    """Test the STARTING event with ecsProperties"""
    print("Testing STARTING event with ecsProperties...")
    
    event = load_test_event("batch-event-STARTING.json")
    
    result = lambda_handler(event, {})
    
    print("Input event:")
    print(json.dumps(event, indent=2))
    print("\nLambda function result:")
    print(json.dumps(result, indent=2))
    
    # Assertions
    assert result['JobId'] == "a58812f1-a6bc-4791-a0ba-26618d74bb33"
    assert result['Region'] == "us-east-1"
    assert result['JobQueue'] == "arn:aws:batch:us-east-1:653295002771:job-queue/batch-job-queue-dev"
    assert result['JobName'] == "cpu-stress-test-1760707009"
    assert result['JobDefinition'] == "arn:aws:batch:us-east-1:653295002771:job-definition/cpu-stress-test-dev:2"
    assert result['LastEventType'] == "STARTING"
    assert result['LastEventTime'] == "2025-10-17T13:19:25Z"
    assert result['isParentArrayJob'] == False
    assert result['containerInstanceArn'] == "arn:aws:ecs:us-east-1:653295002771:container-instance/AWSBatch-batch-compute-env-dev-0a95f22d-7108-3c4e-99f7-2fd92e1a8941/e4ec8ce405b346f8a7b104f695184df7"
    
    print("✅ STARTING event test passed!")
    return result


def test_running_event():
    """Test the RUNNING event"""
    print("\nTesting RUNNING event...")
    
    event = load_test_event("batch-event-RUNNING.json")
    
    result = lambda_handler(event, {})
    
    print("Lambda function result:")
    print(json.dumps(result, indent=2))
    
    # Basic assertions
    assert result['LastEventType'] == "RUNNING"
    assert result['isParentArrayJob'] == False
    assert 'containerInstanceArn' in result
    
    print("✅ RUNNING event test passed!")
    return result


def test_succeeded_event():
    """Test the SUCCEEDED event"""
    print("\nTesting SUCCEEDED event...")
    
    event = load_test_event("batch-event-SUCCEEDED.json")
    
    result = lambda_handler(event, {})
    
    print("Lambda function result:")
    print(json.dumps(result, indent=2))
    
    # Basic assertions
    assert result['LastEventType'] == "SUCCEEDED"
    assert result['isParentArrayJob'] == False
    assert 'containerInstanceArn' in result
    
    print("✅ SUCCEEDED event test passed!")
    return result


def test_array_job_parent():
    """Test a parent array job (should be skipped)"""
    print("\nTesting parent array job...")
    
    # Create a mock parent array job event
    event = load_test_event("batch-event-STARTING.json")
    
    # Modify to make it a parent array job
    event['detail']['arrayProperties'] = {
        "size": 10
    }
    
    result = lambda_handler(event, {})
    
    print("Lambda function result:")
    print(json.dumps(result, indent=2))
    
    # Should be marked as parent array job
    assert result['isParentArrayJob'] == True
    
    print("✅ Parent array job test passed!")
    return result


def test_error_handling():
    """Test error handling with malformed event"""
    print("\nTesting error handling...")
    
    # Empty event
    result = lambda_handler({}, {})
    
    print("Lambda function result for empty event:")
    print(json.dumps(result, indent=2))
    
    # Should handle gracefully
    assert 'error' not in result or result.get('isParentArrayJob') == False
    
    print("✅ Error handling test passed!")
    return result


if __name__ == "__main__":
    print("Running ParseJobAttributesFunction tests...\n")
    
    try:
        test_starting_event()
        test_running_event()
        test_succeeded_event()
        test_array_job_parent()
        test_error_handling()
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)