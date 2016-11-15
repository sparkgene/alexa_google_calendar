# -*- coding: utf-8 -*-

import os
import stat
import urllib
import shutil
import boto3
import json
import datetime
import subprocess

LAMBDA_BASE_DIR = '/var/task' # Lambda fuction can use this directory.
LAMBDA_TMP_DIR = '/tmp' # Lambda fuction can use this directory.
RAW_AUDIO_FILE = "{0}/alexa-sample.wav".format(LAMBDA_TMP_DIR)
CONVERTED_AUDIO_FILE = "{0}/output.mp3".format(LAMBDA_TMP_DIR)
PUBLIC_BUCKET = "my-calendar-audio"

# ffmpeg is stored with this script.
# When executing ffmpeg, execute permission is requierd.
# But Lambda source directory do not have permission to change it.
# So move ffmpeg binary to `/tmp` and add permission.
FFMPEG_BIN = "{0}/ffmpeg".format(LAMBDA_TMP_DIR)
FFMPEG_CONVERT_COMAND = "{} -y -i {} -ac 2 -codec:a libmp3lame -b:a 48k -ar 16000 {}"
shutil.copyfile("{}/ffmpeg.linux64".format(LAMBDA_BASE_DIR), FFMPEG_BIN)
os.environ['IMAGEIO_FFMPEG_EXE'] = FFMPEG_BIN
os.chmod(FFMPEG_BIN, os.stat(FFMPEG_BIN).st_mode | stat.S_IEXEC)


s3 = boto3.client('s3')

def lambda_handler(event, context):
    print(event)

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    print("download_file: {}/{}".format(bucket, key))

    # download raw audio file
    raw_audio_file = "{0}/{1}".format(LAMBDA_TMP_DIR, key)
    new_key = "{}.mp3".format(key.split(".")[0])
    converted_audio_file = "{0}/output-{1}".format(LAMBDA_TMP_DIR, new_key)
    s3.download_file(bucket, key, raw_audio_file)

    # transform audio file to alexa format
    cmd = FFMPEG_CONVERT_COMAND.format(FFMPEG_BIN, raw_audio_file, converted_audio_file)
    ret_code = subprocess.call(cmd, shell=True)
    if ret_code != 0:
        print("convert faild!:{}".format(ret_code))
        return False

    # upload new audio file
    print("upload_file: {}/{}".format(PUBLIC_BUCKET, new_key))
    s3.upload_file(converted_audio_file, PUBLIC_BUCKET, new_key)
    response = s3.put_object_acl(
        ACL="public-read",
        Bucket=PUBLIC_BUCKET,
        Key=new_key
    )

    # remove raw audio file
    response = s3.delete_object(
        Bucket=bucket,
        Key=key
    )

    return True
