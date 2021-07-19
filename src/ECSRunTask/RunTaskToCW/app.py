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
from botocore.exceptions import ClientError
from aws_embedded_metrics import metric_scope
import json
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@metric_scope
def embedded_metrics_placed_jobs(
    dimensions, properties, metric_name, metric_time, metrics):

    try:
        metrics.set_namespace("AWSBatchMetrics")
        logger.info(f"Deactivate metrics.should_use_default_dimensions {metrics.context.should_use_default_dimensions}")
        metrics.context.should_use_default_dimensions = False
        logger.info(f" Done metrics.should_use_default_dimensions {metrics.context.should_use_default_dimensions}")

        # use the event timestamp instead of using the EMF context timestamp
        metric_converted_time = datetime.datetime.strptime(metric_time, '%Y-%m-%dT%H:%M:%SZ')
        metric_converted_time = int(round(metric_converted_time.timestamp()*1000))
        metrics.context.meta['Timestamp'] = metric_converted_time

        for k, v in dimensions.items():
            metrics.put_dimensions({k:v})
        metrics.put_metric(metric_name, 1, "Count")
        for k, v in properties.items():
            metrics.set_property(k, v)

    except ClientError as e:
        message = f"Error adding CloudWatch metric job resubmission: {format(e)}"
        logger.warning(message)
        raise Exception(message)
    return


def lambda_handler(event, context):

    logger.info(f"Transform event to metric {json.dumps(event)}")

    for record in event["Records"]:
        rec = json.loads(record["body"])

        if 'ECSCluster' in rec['Dimensions']: rec['Dimensions']['ECSCluster']   = rec['Dimensions']['ECSCluster'].split('/')[-1].split('_Batch')[0]
        if 'JobQueue'   in rec['Dimensions']: rec['Dimensions']['JobQueue']     = rec['Dimensions']['JobQueue'].split('/')[-1]
        
        if 'ECSCluster' in rec['Properties']: rec['Properties']['ECSCluster']   = rec['Properties']['ECSCluster'].split('/')[-1].split('_Batch')[0]
        if 'JobQueue'   in rec['Properties']: rec['Properties']['JobQueue']     = rec['Properties']['JobQueue'].split('/')[-1]
        
        embedded_metrics_placed_jobs(
            rec["Dimensions"],
            rec["Properties"],
            rec['MetricName'],
            rec["MetricTime"])

    logger.info(f"Metrics sent to EMF")


    return
