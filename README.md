# alexa_google_calendar
Google calendar Alexa Skill.

https://www.hackster.io/sparkgene/how-to-make-alexa-speak-your-language-24c091

## Overview

This is a project for Amazon Alexa to speak un-supported language.

## Installation

```
git clone https://github.com/sparkgene/alexa_google_calendar
```

## setup

### Create Amazon DynamoDB table.

  ``` shell
  aws dynamodb create-table --table-name calendar_event \
  --attribute-definitions AttributeName=uid,AttributeType=S AttributeName=begin_date,AttributeType=S \
  --key-schema AttributeName=uid,KeyType=HASH AttributeName=begin_date,KeyType=RANGE \
  --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1
```

### create lambda function role

create a role which have following policy

```
{
   "Version": "2012-10-17",
   "Statement": [
       {
           "Sid": "lambdacalendarskill1",
           "Effect": "Allow",
           "Action": [
               "logs:CreateLogGroup",
               "logs:CreateLogStream",
               "logs:PutLogEvents"
           ],
           "Resource": "arn:aws:logs:*:*:*"
       },
       {
           "Sid": "lambdacalendarskill2",
           "Effect": "Allow",
           "Action": [
               "s3:GetObject",
               "s3:GetObjectAcl",
               "s3:ListBucket",
               "s3:PutObject",
               "s3:PutObjectAcl",
               "s3:DeleteObject"
           ],
           "Resource": [
               "arn:aws:s3:::my-calendar-raw-audio",
               "arn:aws:s3:::my-calendar-raw-audio/*",
               "arn:aws:s3:::my-calendar-audio",
               "arn:aws:s3:::my-calendar-audio/*"
           ]
       },
       {
           "Sid": "lambdacalendarskill3",
           "Action": [
               "dynamodb:GetItem",
               "dynamodb:PutItem",
               "dynamodb:UpdateItem",
               "dynamodb:Scan",
               "lambda:InvokeFunction"
           ],
           "Effect": "Allow",
           "Resource": "*"
       }
   ]
}
```

This project need 3 lambda function to generate audio file.

![diagram](https://raw.githubusercontent.com/sparkgene/alexa_google_calendar/master/diagram.png)

### calendar crawler

This function get google calendar ics data. Parse it and store to DynamoDB. After storing the calendar data, invoke the audio generate lambda function.

https://github.com/sparkgene/alexa_google_calendar/blob/master/lambda_calendar_crawler

### text to speech

You have two way to generate audio data.

#### Amazon Polly

This function use Amazon Polly togenerate audio data from calendar summury. Generated data is stored in Amazon S3 bucket.

https://github.com/sparkgene/alexa_google_calendar/tree/master/lambda_calendar_text_to_speech_polly

if you want to use another language, Change the parameter "VoiceId".

```
response = polly.synthesize_speech(
        Text=event["summary"],
        OutputFormat="mp3",
        SampleRate="16000",
        VoiceId="Mizuki")
```

#### IBM Text to Speech service

This function use IBM Text to Speech service to generate audio data from calendar summury. Generated data is stored in Amazon S3 bucket.

https://github.com/sparkgene/alexa_google_calendar/tree/master/lambda_calendar_text_to_speech

if you want to use another language, Change the parameter "voice".

```
raw_data = text_to_speech.synthesize(event["summary"], accept='audio/wav', voice="ja-JP_EmiVoice")
Check the supported voice type at here.
```

https://www.ibm.com/watson/developercloud/text-to-speech/api/v1/?curl#get_voice  

### audio transform

This function invoked from S3 events. Convert audio data to Alexa required format and store in another Amazon S3 bucket.

https://github.com/sparkgene/alexa_google_calendar/tree/master/lambda_audio_transform

### Alexa Skill

The Alexa Skill for asking calendar events.

https://github.com/sparkgene/alexa_google_calendar/tree/master/lambda_calendar_skill
