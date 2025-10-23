import json
import boto3


def get_main_node_status(child_job_id, region):
    """
    Get the status of the main node for an MNP job given a child job ID.
    
    Args:
        child_job_id: The child job ID (e.g., "job-id#1")
        region: AWS region
        
    Returns:
        str: Main node status or None if not found
    """
    try:
        if not child_job_id or '#' not in child_job_id:
            return None
            
        # Extract the base job ID (remove node index)
        base_job_id = child_job_id.split('#')[0]
        main_job_id = f"{base_job_id}#0"  # Main node is always index 0
        
        # Create Batch client
        batch_client = boto3.client('batch', region_name=region)
        
        # Describe the main job
        response = batch_client.describe_jobs(jobs=[main_job_id])
        
        if response.get('jobs') and len(response['jobs']) > 0:
            main_job = response['jobs'][0]
            return main_job.get('status')
            
        return None
        
    except Exception as e:
        print(f"Error getting main node status: {str(e)}")
        return None


def lambda_handler(event, context):
    """
    Parse AWS Batch job state change event attributes and determine if it's from a parent array job.
    
    Args:
        event: The input from the state machine containing the job state change event
        
    Returns:
        dict: Parsed job attributes with isParentArrayJob flag
    """
    
    try:
        # Extract the detail from the event
        detail = event.get('detail', {})
        
        # Parse core job attributes
        job_attributes = {
            'JobId': detail.get('jobId'),
            'Region': event.get('region'),
            'JobQueue': detail.get('jobQueue'),
            'JobName': detail.get('jobName'),
            'JobDefinition': detail.get('jobDefinition'),
            'LastEventType': detail.get('status'),
            'LastEventTime': event.get('time')
        }
        
        # Check if this is a parent array job
        is_parent_array_job = False
        array_properties = detail.get('arrayProperties')
        
        if array_properties and 'size' in array_properties:
            # If arrayProperties contains 'size', this is a parent array job
            is_parent_array_job = True
        
        # Check if this is a multi-node parallel (MNP) job child node
        is_mnp_child_node = False
        node_details = detail.get('nodeDetails')
        original_status = detail.get('status')
        
        if node_details:
            # This is an MNP job - check if it's a child node
            is_main_node = node_details.get('isMainNode', False)
            if not is_main_node:
                # This is a child node
                is_mnp_child_node = True
                
                # If child node failed, query main node status
                if original_status == 'FAILED':
                    main_node_status = get_main_node_status(detail.get('jobId'), event.get('region'))
                    if main_node_status:
                        # Override the status with main node status
                        job_attributes['LastEventType'] = main_node_status
                        print(f"MNP child node {detail.get('jobId')} failed, using main node status: {main_node_status}")
        
        # Determine container instance ARN
        container_instance_arn = None
        
        # First check direct container path (single-container jobs)
        container = detail.get('container', {})
        if container.get('containerInstanceArn'):
            container_instance_arn = container['containerInstanceArn']
        
        # Check ecsProperties for multi-container jobs
        elif detail.get('ecsProperties'):
            # For multi-container jobs, containerInstanceArn is in ecsProperties.taskProperties[0].containerInstanceArn
            ecs_properties = detail.get('ecsProperties', {})
            task_properties = ecs_properties.get('taskProperties', [])
            if task_properties and len(task_properties) > 0:
                container_instance_arn = task_properties[0].get('containerInstanceArn')
        
        # If not found, check attempts array for container instance ARN
        if not container_instance_arn:
            attempts = detail.get('attempts', [])
            if attempts:
                # Get the last attempt
                last_attempt = attempts[-1]
                
                # Check container in attempts (single-container)
                attempt_container = last_attempt.get('container', {})
                if attempt_container.get('containerInstanceArn'):
                    container_instance_arn = attempt_container['containerInstanceArn']
                
                # Check taskProperties in attempts (multi-container)
                elif last_attempt.get('taskProperties'):
                    attempt_task_properties = last_attempt.get('taskProperties', [])
                    if attempt_task_properties and len(attempt_task_properties) > 0:
                        container_instance_arn = attempt_task_properties[0].get('containerInstanceArn')
        
        # Add parsed attributes to response
        result = {
            **job_attributes,
            'isParentArrayJob': is_parent_array_job,
            'isMnpChildNode': is_mnp_child_node,
            'containerInstanceArn': container_instance_arn
        }
        
        return result
        
    except Exception as e:
        # Return error information for debugging
        return {
            'error': str(e),
            'isParentArrayJob': False,
            'isMnpChildNode': False,
            'containerInstanceArn': None
        }