import json

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
            'containerInstanceArn': container_instance_arn
        }
        
        return result
        
    except Exception as e:
        # Return error information for debugging
        return {
            'error': str(e),
            'isParentArrayJob': False,
            'containerInstanceArn': None
        }