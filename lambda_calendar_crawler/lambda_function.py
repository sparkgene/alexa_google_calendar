# coding=utf-8

import os
import json
import boto3
import time
import hashlib
from ics import Calendar
from urllib2 import urlopen
from datetime import datetime, timedelta

GOOGLE_CALENDAR_URL = os.environ["GOOGLE_CALENDAR_URL"]
DYNAMODB_TABLE_NAME = "calendar_event"
TEXT_TO_SPEECH_LAMBDA = os.environ["TEXT_TO_SPEECH_LAMBDA"]
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]

s3 = boto3.resource('s3')
bucket = s3.Bucket(AUDIO_BUCKET)

def load_events():
    cal = Calendar(urlopen(GOOGLE_CALENDAR_URL).read().decode('utf-8'))

    cal_events = []
    today = datetime.now() + timedelta(hours=9)
    dt_from = datetime(today.year, today.month, today.day, hour=0, minute=0, second=0, microsecond=0)
    for event in cal.events:
        event_start = datetime.fromtimestamp(event.begin.timestamp) + timedelta(hours=9)
        if event_start < dt_from:
            continue
        cal_events.append(
            {
                "begin_date": event_start.strftime("%Y-%m-%d"),
                "begin_hour": event_start.strftime("%H"),
                "summary": event.name,
                "uid": hashlib.sha1(event.name).hexdigest()
            }
        )
    return cal_events

def store_event(events):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    add_events = []
    for event in events:
        result = table.get_item(
            Key={
                'uid': event["uid"],
                "begin_date": event["begin_date"]
            }
        )

        if 'Item' not in result:
            table.put_item(
                Item={
                    "uid": event["uid"],
                    "begin_date": event["begin_date"],
                    "begin_hour": event["begin_hour"],
                    "summary": event["summary"]
                }
            )
            add_events.append(
                {
                    "uid": event["uid"],
                    "summary": event["summary"]
                }
            )
            print("event add:{}".format(event["summary"]))

        elif not result['Item']['begin_date'] == event["begin_date"] or \
          not result['Item']['begin_hour'] == event["begin_hour"] or \
          not result['Item']['summary'] == event["summary"]:
            table.put_item(
                Item={
                    "uid": event["uid"],
                    "begin_date": event["begin_date"],
                    "begin_hour": event["begin_hour"],
                    "summary": event["summary"]
                }
            )
            add_events.append(
                {
                    "uid": event["uid"],
                    "summary": event["summary"]
                }
            )
            print("event update:{}".format(event["summary"]))

        time.sleep(1)

    return add_events

def lambda_handler(event, context):

    events = load_events()
    add_events = store_event(events)
    if len(add_events) > 0:
        client = boto3.client('lambda')
        response = client.invoke(
            FunctionName=TEXT_TO_SPEECH_LAMBDA,
            InvocationType='Event',
            Payload=json.dumps(add_events)
        )

    return True
