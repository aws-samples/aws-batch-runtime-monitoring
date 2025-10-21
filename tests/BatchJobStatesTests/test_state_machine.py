#!/usr/bin/env python3
"""
Test script for JobStatesStateMachineServerless state machine logic
This simulates the state machine execution flow without AWS Step Functions
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


def simulate_get_common_fields(event):
    """Simulate the 'Get Common Fields' Pass state"""
    return {
        "JobId": event['detail']['jobId'],
        "Region": event['region'],
        "JobQueue": event['detail']['jobQueue'],
        "JobName": event['detail']['jobName'],
        "JobDefinition": event['detail']['jobDefinition'],
        "LastEventType": event['detail']['status'],
        "LastEventTime": event['time'],
        "Execution": {
            "Input": event
        }
    }


def simulate_check_job_state(state_data):
    """Simulate the 'Check Job State' Choice state"""
    valid_states = ["SUCCEEDED", "FAILED", "RUNNING", "STARTING"]
    
    if state_data["LastEventType"] in valid_states:
        return "Parse Job Attributes"
    else:
        return "SQS SendMessage Job State Not Associated"


def simulate_parse_job_attributes(state_data):
    """Simulate the 'Parse Job Attributes' Lambda invocation"""
    # Call the actual Lambda function
    lambda_result = lambda_handler(state_data["Execution"]["Input"], {})
    
    # Simulate the ResultSelector behavior
    return {
        "JobId": lambda_result["JobId"],
        "Region": lambda_result["Region"],
        "JobQueue": lambda_result["JobQueue"],
        "JobName": lambda_result["JobName"],
        "JobDefinition": lambda_result["JobDefinition"],
        "LastEventType": lambda_result["LastEventType"],
        "LastEventTime": lambda_result["LastEventTime"],
        "isParentArrayJob": lambda_result["isParentArrayJob"],
        "containerInstanceArn": lambda_result["containerInstanceArn"]
    }


def simulate_check_if_parent_array_job(state_data):
    """Simulate the 'Check If Parent Array Job' Choice state"""
    if state_data.get("isParentArrayJob") == True:
        return "Skip Event"
    else:
        return "Check Container Instance ARN"


def simulate_check_container_instance_arn(state_data):
    """Simulate the 'Check Container Instance ARN' Choice state"""
    if state_data.get("containerInstanceArn"):
        return "DynamoDB GetItem EC2 InstanceId from ContainerInstanceId"
    else:
        return "Skip Event"


def simulate_state_machine_execution(event):
    """Simulate the complete state machine execution"""
    print(f"🚀 Starting state machine simulation for {event['detail']['status']} event")
    
    # Step 1: Get Common Fields
    print("📝 Step 1: Get Common Fields")
    state_data = simulate_get_common_fields(event)
    print(f"   State data: {json.dumps(state_data, indent=2)}")
    
    # Step 2: Check Job State
    print("\n🔍 Step 2: Check Job State")
    next_state = simulate_check_job_state(state_data)
    print(f"   Next state: {next_state}")
    
    if next_state == "SQS SendMessage Job State Not Associated":
        print("   ⚠️  Job state not in valid states, would send unassociated message")
        return "SQS SendMessage Job State Not Associated", state_data
    
    # Step 3: Parse Job Attributes
    print("\n🔧 Step 3: Parse Job Attributes")
    state_data = simulate_parse_job_attributes(state_data)
    print(f"   Parsed attributes: {json.dumps(state_data, indent=2)}")
    
    # Step 4: Check If Parent Array Job
    print("\n👨‍👩‍👧‍👦 Step 4: Check If Parent Array Job")
    next_state = simulate_check_if_parent_array_job(state_data)
    print(f"   Next state: {next_state}")
    
    if next_state == "Skip Event":
        print("   ⏭️  Parent array job detected, skipping event")
        return "Skip Event", state_data
    
    # Step 5: Check Container Instance ARN
    print("\n🖥️  Step 5: Check Container Instance ARN")
    next_state = simulate_check_container_instance_arn(state_data)
    print(f"   Next state: {next_state}")
    
    if next_state == "Skip Event":
        print("   ⏭️  No container instance ARN found, skipping event")
        return "Skip Event", state_data
    
    # If we get here, we would proceed to DynamoDB lookup
    print("   ✅ Container instance ARN found, would proceed to DynamoDB lookup")
    return "DynamoDB GetItem EC2 InstanceId from ContainerInstanceId", state_data


def test_starting_event_flow():
    """Test the complete flow with STARTING event"""
    print("=" * 60)
    print("Testing STARTING event flow")
    print("=" * 60)
    
    event = load_test_event("batch-event-STARTING.json")
    final_state, final_data = simulate_state_machine_execution(event)
    
    print(f"\n🏁 Final state: {final_state}")
    print(f"📊 Final data keys: {list(final_data.keys())}")
    
    # Assertions
    assert final_state == "DynamoDB GetItem EC2 InstanceId from ContainerInstanceId"
    assert final_data["containerInstanceArn"] is not None
    assert final_data["isParentArrayJob"] == False
    
    print("✅ STARTING event flow test passed!")
    return final_state, final_data


def test_parent_array_job_flow():
    """Test the flow with a parent array job (should skip)"""
    print("\n" + "=" * 60)
    print("Testing parent array job flow")
    print("=" * 60)
    
    event = load_test_event("batch-event-STARTING.json")
    
    # Modify to make it a parent array job
    event['detail']['arrayProperties'] = {
        "size": 10
    }
    
    final_state, final_data = simulate_state_machine_execution(event)
    
    print(f"\n🏁 Final state: {final_state}")
    
    # Should skip the event
    assert final_state == "Skip Event"
    assert final_data["isParentArrayJob"] == True
    
    print("✅ Parent array job flow test passed!")
    return final_state, final_data


def test_invalid_job_state_flow():
    """Test the flow with invalid job state"""
    print("\n" + "=" * 60)
    print("Testing invalid job state flow")
    print("=" * 60)
    
    event = load_test_event("batch-event-STARTING.json")
    
    # Change to invalid state
    event['detail']['status'] = "INVALID_STATE"
    
    final_state, final_data = simulate_state_machine_execution(event)
    
    print(f"\n🏁 Final state: {final_state}")
    
    # Should go to unassociated message
    assert final_state == "SQS SendMessage Job State Not Associated"
    
    print("✅ Invalid job state flow test passed!")
    return final_state, final_data


if __name__ == "__main__":
    print("Running State Machine simulation tests...\n")
    
    try:
        test_starting_event_flow()
        test_parent_array_job_flow()
        test_invalid_job_state_flow()
        
        print("\n" + "🎉" * 20)
        print("All state machine tests passed!")
        print("🎉" * 20)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)