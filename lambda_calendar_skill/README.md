# lambda_calendar_skill
Alexa Skill for google calendar.

## Overview

This lambda function get google calendar data(ics file).
It store event information in DynamoDB.
If the event is not changed(begin date, start hour, summary), it do nothing.

## Installation

Create a Lambda function and paste the lambda_function.py in to code.
