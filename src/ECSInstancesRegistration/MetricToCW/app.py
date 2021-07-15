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
import json
from botocore.exceptions import ClientError
from aws_embedded_metrics import metric_scope
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@metric_scope
def emf_instance_registration(availability_zone, ecs_cluster,
                              instance_type, instance_id, metric_name,
                              metric_time, metrics):

    logger.info(f"Adding metric for {instance_id} for {ecs_cluster}")
    ecs_cluster = ecs_cluster.split('/')[-1].split('_Batch')[0]

    # use the event timestamp instead of using the EMF context timestamp
    metric_converted_time = datetime.datetime.strptime(metric_time, '%Y-%m-%dT%H:%M:%SZ')
    metric_converted_time = int(round(metric_converted_time.timestamp()*1000))
    metrics.context.meta['Timestamp'] = metric_converted_time

    try:
        metrics.set_namespace("AWSBatchMetrics")
        metrics.set_dimensions({
            "AvailabilityZone": availability_zone
        }, {
            "ECSCluster": ecs_cluster
        }, {
            "InstanceType": instance_type
        })
        metrics.put_metric(metric_name, 1, "Count")
        metrics.set_property("InstanceId", instance_id)
        metrics.set_property("ECSCluster", ecs_cluster)
        metrics.set_property("InstanceType", instance_type)
        metrics.set_property("AvailabilityZone", availability_zone)

    except ClientError as e:
        message = f"Error adding CloudWatch metric job resubmission: {format(e)}"
        logger.warning(message)
        raise Exception(message)
    return

def lambda_handler(event, context):
    logger.info(f"Transform event to metric {event}")

    for record in event["Records"]:
        rec = json.loads(record["body"])

        emf_instance_registration(
            rec["Dimensions"]['AvailabilityZone'],
            rec["Dimensions"]['ECSCluster'],
            rec["Dimensions"]['InstanceType'],
            rec["Properties"]['InstanceId'],
            rec['LastEventType'],
            rec['MetricTime'])
    logger.info(f"Metrics to send to EMF")

    return
