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

from botocore.exceptions import ClientError
import logging
import boto3
import os
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

firehose = boto3.client('firehose')
jobs_states_stream = os.environ['JOBS_STATES_STREAM']

def lambda_handler(event, context):

    logger.info(f"processing event {json.dumps(event)}")

    records = []
    for record in event["Records"]:
        rec = json.loads(record["body"])
        records.append({"Data": json.dumps(rec)})

    logger.info(f"Exporting records {records}")


    try:
        # Send Event to Firehose
        response = firehose.put_record_batch(
            DeliveryStreamName=jobs_states_stream,
            Records=records
        )
        logger.info(response)

    except ClientError as e:
        message = f"Error sending event data to Kinesis Firehose: {e}"
        logger.info(message)
        raise Exception(message)

    return
