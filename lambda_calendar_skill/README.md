# lambda_calendar_skill
Alexa Skill for google calendar.

## configuration

set these Environment variables on lambda function.

### APP_ID

Skill app id.

### CALENDAR_NAME

calendar name will used in the text.

### S3_AUDIO_BUCKET

audio bucket(public)

## Overview

This lambda function get google calendar data(ics file).
It store event information in DynamoDB.
If the event is not changed(begin date, start hour, summary), it do nothing.

## Installation

Create a Lambda function and paste the lambda_function.py in to code.
