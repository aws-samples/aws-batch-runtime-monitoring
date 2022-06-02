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
import json
import sched
from aws_embedded_metrics import metric_scope

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@metric_scope
def submit_job_stats(rec, metrics):
    metrics.context.should_use_default_dimensions = False
    metrics.set_namespace("AWSBatchMetrics")
    # summary stats are registered at job stopped time
    metrics.context.meta["Timestamp"] = rec["detail"]["stoppedAt"]
    if 'ECSCluster' in rec['Properties']:
        ecs_cluster = rec['Properties']['ECSCluster'].split('/')[-1].split('_Batch')[0]
        rec['Properties']['ECSCluster'] = ecs_cluster

    if 'ECSCluster' in rec['Dimensions']:
        ecs_cluster = rec['Dimensions']['ECSCluster'].split('/')[-1].split('_Batch')[0]
        rec['Dimensions']['ECSCluster'] = ecs_cluster

    if 'JobQueue' in rec['Properties']:
        job_queue = rec['Properties']['JobQueue'].split('/')[-1]
        rec['Properties']['JobQueue'] = job_queue

    if 'JobQueue' in rec['Dimensions']:
        job_queue = rec['Dimensions']['JobQueue'].split('/')[-1]
        rec['Dimensions']['JobQueue'] = job_queue

    if 'JobDefinition' in rec['Properties']:
        job_queue = rec['Properties']['JobDefinition'].split('/')[-1]
        rec['Properties']['JobDefinition'] = job_queue

    if 'JobDefinition' in rec['Dimensions']:
        job_queue = rec['Dimensions']['JobDefinition'].split('/')[-1]
        rec['Dimensions']['JobDefinition'] = job_queue

    waitTime = rec["detail"]["startedAt"]-rec["detail"]["createdAt"]
    runTime = rec["detail"]["stoppedAt"]-rec["detail"]["startedAt"] 
    totalTime = rec["detail"]["stoppedAt"]-rec["detail"]["createdAt"] 
    schedEfficiency = (rec["detail"]["stoppedAt"]-rec["detail"]["startedAt"])/(rec["detail"]["stoppedAt"]-rec["detail"]["createdAt"])*100 
    for k, v in rec['Dimensions'].items():
        metrics.put_dimensions({k:v})
    metrics.put_metric("WaitTime", waitTime, "Milliseconds")
    metrics.put_metric("RunTime", runTime, "Milliseconds")
    metrics.put_metric("TotalTime", totalTime, "Milliseconds")
    metrics.put_metric("SchedulingEfficiency", schedEfficiency, "Percent")
    for k, v in rec['Properties'].items():
        metrics.set_property(k, v)
    logger.info(f"Wrote WaitTime {waitTime} RunTime {runTime} TotalTime {totalTime} SchedulingEfficiency {schedEfficiency}")


def lambda_handler(event, context):
    logger.info(f"Create job summary statistic metrics {json.dumps(event)}")

    for record in event["Records"]:
        try:
            rec = json.loads(record["body"])
            submit_job_stats(rec)
        except Exception as e:
            logger.error(f"Caught exception submitting record: {e}")

    logger.info(f"Submitted {len(event['Records'])} records")