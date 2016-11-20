# coding=utf-8

import os
import json
import boto3
import time
from watson_developer_cloud import TextToSpeechV1

WATSON_USER_NAME = os.environ["WATSON_USER_NAME"]
WATSON_PASSWORD = os.environ["WATSON_PASSWORD"]
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]

s3 = boto3.resource('s3')
bucket = s3.Bucket(AUDIO_BUCKET)

def create_audio(events):
    text_to_speech = TextToSpeechV1(
        username=WATSON_USER_NAME,
        password=WATSON_PASSWORD,
        x_watson_learning_opt_out=True)

    for event in events:
        raw_data = text_to_speech.synthesize(event["summary"], accept='audio/wav', voice="ja-JP_EmiVoice")
        if is_json(raw_data):
            continue
        store_audio(raw_data, event["uid"])
        time.sleep(1)

def store_audio(data, uid):
    obj = bucket.Object("{}.wav".format(uid))
    response = obj.put(
        Body=data,
        ContentType="audio/wav"
    )
    print(response)

def is_json(data):
    try:
        json_object = json.loads(data)
    except ValueError, e:
        return False
    print(json_object)
    return True

def lambda_handler(event, context):

    print(event)
    if len(event) > 0:
        create_audio(event)

    return True
