# AWS Batch Runtime Monitoring Dashboards Solution

This [SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) application deploys a [serverless architecture](https://aws.amazon.com/lambda/serverless-architectures-learn-more/) to capture events from Amazon ECS, AWS Batch and Amazon EC2 to visualize the behavior of your workloads running on AWS Batch and provide insights on your jobs and the instances used to run them.

This application is designed to be scalable by collecting data from events and API calls using Amazon EventBrige and does not make API calls to describe your resources. Data collected through events and API are partially aggregated to DynamoDB to recoup information and generate Amazon CloudWatch metrics with the [Embedded Metric Format](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Embedded_Metric_Format.html). The application also deploys a several of dashboards displaying the job states, Amazon EC2 instances belonging your Amazon ECS Clusters (AWS Batch Compute Environments), ASGs across Availability Zones. It also collects API calls to the *RunTask* to visualize job placement across instances.

## Dashboard

A series of dashboards are deployed as part of the SAM application. They provide information on your ASGs scaling, the capacity in vCPUs and instances. You will also find dashboards providing statistics on Batch job states transitions, RunTask API calls and jobs placement per Availability Zone, Instance Type, Job Queue and ECS Cluster.

![Alt text](docs/jobs_transitions.png?raw=true "Jobs Transitions Dashboard")

## Architecture Diagram

![Alt text](docs/architecture.png?raw=true "Architecture Diagram")

## Overview

This solution captures events from AWS Batch and Amazon ECS using Amazon Event Bridge. Each event triggers an Amazon Lambda function that will add a metrics in Amazon CloudWatch and interact with an Amazon DynamoDB table to tie a job to the instance it runs on.

- **ECS Instance Registration**: captures when instance are [added](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_RegisterContainerInstance.html) or [removed](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_DeregisterContainerInstance.html) from an ECS cluster ([Compute Environments](https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html) in Batch). It helps to link together the EC2 Instance ID and the ECS Container Instance ID.
- **ECS RunTask**: is the [API](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_RunTask.html) called by AWS Batch to run the jobs. Calls can be successful (job placed on the cluster) or not in which case the job is not placed due to a lack of free resources.
- **Batch Job Transitions**: capture Batch jobs transitions between [states](https://docs.aws.amazon.com/batch/latest/userguide/job_states.html) and their placement across Job Queues and Compute Environments.

DynamoDB is used to retain state of the instances joining the ECS Clusters (which sit underneath our Batch Compute Environments) so we can identify the instances joining a cluster and in which availability zone they are created. This also allows us to identify on which instance jobs are placed, succeed or fail.

When RunTask is called or Batch jobs transition between state, we can associate them to the Amazon EC2 instance on which they are running. *RunTask API* calls and Batch jobs are not associated directly with Amazon EC2, we use the `ContainerInstanceID` generated when an instance registers with a cluster to identify which Amazon EC2 instance is used to run a job (or place a task in the case of ECS). This architecture does not make any explicit API call such as `DescribeJobs` or `DescribeEC2Instance` which makes it it relatively scalable and not subject to potential [throttling](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/throttling.html) on these APIs.

[CloudWatch Embedded Metrics Format (EMF)](https://github.com/awslabs/aws-embedded-metrics-python) is used to collect the metrics displayed on the dashboards. Step Function are used to build the logic around the Lamba functions handing the events and data stored in DynamoDB and pushed to CloudWatch EMF.

## How to run the SAM application

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --guided
```

You will be asked to provide a few parameters.

Parameters
---
When creating the stack for the first time you will need to provide the following parameters:

- **Stack Name**: name of the CloudFormation stack that will be deployed.
- **AWS Region**: region in which you will deploy the stack, the default region will be used if nothing is provided.
- **CreateTrail**: this parameter enables the creation of an AWS CloudTrail trail in your account. Two possible settings are available for this parameter. Select:
    - `yes`: if you want to create a new AWS CloudTrail trail;
    - `no`: if you want to proceed without the AWS CloudTrail trail creation.
    
    To work properly, the tool needs *at least* one AWS CloudTrail trail with the following characteristics in your AWS Account:
    - trail logging must be on;
    - it must record "Management Events";
    - API Activity must be set both to *read* and *write*;
    - it must be a multi-region trail or deployed in the same AWS Region of the tool.
    
    If you already have a trail with the above-mentioned characteristics, you can avoid deploying another trail; thus, you can set the CreateTrail parameter to `no`.
    If not, or if you are not sure, set the parameter to `yes`.

    You can check if you already have deployed an AWS CloudTrail trail which fits all the requirements of the tool through the AWS Console by selecting: 
    - AWS CloudTrail page;
    - Trails;
    - in this section, you can find your AWS account's trails. Thus for moving into the next step, you are looking for a trail which the status is "logging" and has multi-region enabled *or* that is deployed in the same region as the tool;
    - by clicking the trail name you can find the "Management events" panel that contains the "API activity" field. To match the requirements the "Management events" panel must be active and the "API activity" field must be equal to "All".

    Or, if you preferer, with the AWS CLI:
    - list all your tails and check the multi-region parameter or the AWS region of deployment. For moving into the next steps, you are looking for a trail that has multi-region enabled *or* that is deployed in the same region as the tool;
      ```bash
      aws cloudtrail describe-trails # provides you the list of all the trails in your account with information about ARN, region and multi-region deployement
      ```
      example of output with one trail:
      ```json
      {
      "trailList": [
          {
              "Name": "YOUR_TRAIL_NAME",
              "IsMultiRegionTrail": "MULTI-REGION_boolean",
              "HomeRegion": "YOUR_TRAIL_REGION",
              "TrailARN": "YOUR_TRAIL_ARN",
              "_comment": "And many other attributes"
          }
      ]
      }
      ```
    - check if the trail is logging the events. For moving into the next step it must be `true`;
      ```bash
      aws cloudtrail get-trail-status --name YOUR_TRAIL_ARN # provides you the status of the trail. Here we can check the logging status
      ```
      example of output:
      ```json
      {
          "IsLogging": "LOGGIN_STATUS_boolean",
          "_comment": "And many other attributes"
      }
      ```
    - check which events the trail is recording. We look for a trail which records read and write "API Activity" of "Management events": 
      ```bash
      aws cloudtrail get-event-selectors --trail-name YOUR_TRAIL_ARN # provides you the details about the trail Event Selector
      ```
      example of two trails - more than one syntax is possible - with "Management events" enabled, more about [Event Selector](https://docs.aws.amazon.com/awscloudtrail/latest/APIReference/API_EventSelector.html):
      ```json
      {
          "TrailARN": "YOUR_TRAIL_ARN",
          "AdvancedEventSelectors": [
              {
                  "Name": "Management events selector",
                  "FieldSelectors": [
                      {
                          "Field": "eventCategory",
                          "Equals": [
                              "Management"
                          ]
                      }
                  ]
              }
          ]
      }
      -------------------------------------------------
      {
      "TrailARN": "YOUR_TRAIL_ARN",
      "EventSelectors": [
          {
              "ReadWriteType": "All",
              "IncludeManagementEvents": true,
              "DataResources": [],
              "ExcludeManagementEventSources": []
          }
      ]
      }
      ```

    

After the first launch, you can modify the function and deploy a new version with the same parameters through the following commands:

```bash
sam build
sam deploy # use sam deploy --no-confirm-changeset to force the deployment without validation
```

Cleanup
---

If you didn't set SAM's CreateTrail parameter to `yes` *skip* the following step: 
- AWS Console:
  - go to the Amazon Simple Storage Service page;
  - look for a bucket called `STACK_NAME-s3cloudtrailbucket-([a-zA-Z0-9_-])*`, for example: `My-Monitoring-Stack-s3cloudtrailbucket-1k2hb0mebxnix`;
  - open that bucket and empty it.
- AWS CLI: 
  - run `aws s3 ls` to list all the S3 bucket of your account;
  - look for a bucket called `STACK_NAME-s3cloudtrailbucket-([a-zA-Z0-9_-])*`, for example: `My-Monitoring-Stack-s3cloudtrailbucket-1k2hb0mebxnix`;
  - run `aws s3 rm s3://BUCKET_NAME --recursive` to empy the bucket.

Now, to remove the SAM application, go to the CloudFormation page of the AWS Console, select your stack and click **Delete** or execute the following AWS CLI command: `aws cloudformation delete-stack --stack-name STACK_NAME --region AWS_REGION`.

Adding Monitoring to Existing Auto-Scaling Groups
---
The Clusters Usage dashboards needs monitoring activated for each Auto-Scaling groups (ASGs), it is not done by default. The `ASGMonitoring` Lambda function in the serverless application automatically adds monitoring for new ASGs created by AWS Batch but to add it for existing ones you can run the following command in your terminal (install `jq`) or [AWS CloudShell](https://console.aws.amazon.com/cloudshell):

```bash
aws autoscaling describe-auto-scaling-groups | \
  jq -c '.AutoScalingGroups[] | select(.MixedInstancesPolicy.LaunchTemplate.LaunchTemplateSpecification.LaunchTemplateName | contains("Batch-lt")) | .AutoScalingGroupName' | \
  xargs -t -I {} aws autoscaling enable-metrics-collection  \
    --metrics GroupInServiceCapacity GroupDesiredCapacity GroupInServiceInstances \
    --granularity "1Minute" \
    --auto-scaling-group-name {}
```

### Requirements

To run the serverless application you need to install the [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) and have Python 3.8 installed on your host. Python 3.7 can be used as well by modifying the `template.yaml` file and replace the Lambda functions runtime from `python3.8` to `python3.7`. You can quickly do this with the following `sed` command in the repository directory:


```bash
sed -i 's/3\.8/3\.7/g' template.yaml
```

If you plan to use [AWS CloudShell](https://aws.amazon.com/cloudshell/) to deploy the SAM template, please modify the Lambda runtime to `3.7` as suggested above (unless `3.8` is available) and make your Python 3 command the default for `python`: `alias python=/usr/bin/python3.7`. You can check the Python version available in CloudShell with `python3 --version`.

## References

- https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
- https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-function.html
- https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-policy-templates.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_cwe_events.html
- https://docs.aws.amazon.com/batch/latest/userguide/batch_cwe_events.html
