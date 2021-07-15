# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    # show the response
    logger.info(event)

    # get our ASG client
    client = boto3.client('autoscaling')

    # get the list of autoscaling groups
    resp = client.describe_auto_scaling_groups()

    # if the ASG is created by Batch enable metrics collection
    for g in resp['AutoScalingGroups']:
        try:
            x = g['MixedInstancesPolicy']['LaunchTemplate']['LaunchTemplateSpecification']['LaunchTemplateName']

        except Exception:
            logger.info(f"Cannot add metrics collection for {g['AutoScalingGroupName']}")

        if 'Batch-lt' in x and 'EnabledMetrics' in g:
            # in our case we add all the metrics but you could select the ones of interest
            # don't forget to check and update your dashboards should you change the metrics
            # https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-instance-monitoring.html
            r = client.enable_metrics_collection(AutoScalingGroupName=g['AutoScalingGroupName'], Granularity='1Minute')
            logger.info(f"Enabled metrics collection on {g['AutoScalingGroupName']}")

    return
