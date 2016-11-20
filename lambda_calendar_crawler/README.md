# lambda_calendar_crawler
Get events information from google calendar.

## Overview

This lambda function get google calendar data(ics file).
It store event information in DynamoDB.
If the event is not changed(begin date, start hour, summary), it do nothing.

## configuration

set these Environment variables on lambda function.

### GOOGLE_CALENDAR_URL

the url of ics file

### TEXT_TO_SPEECH_LAMBDA

the lambda function name which generate audio file from text.

### AUDIO_BUCKET

S3 audio bucket(private)

## Installation

```
cd lambda_calendar_crawler
pip install -r requirements.txt -t $(pwd)
```

compress all files in to zip.
```
zip -r func.zip .
```

upload zip file to lambda function.

This function use long time to convert data.
Set the timeout to 5 minuets.

Create cloudwatch event - schedule to invoke this function daily.

## Create Amazon DynamoDB table.

  ``` shell
  # create table
  aws dynamodb create-table --table-name calendar_event \
  --attribute-definitions AttributeName=uid,AttributeType=S AttributeName=begin_date,AttributeType=S \
  --key-schema AttributeName=uid,KeyType=HASH AttributeName=begin_date,KeyType=RANGE \
  --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1
```
