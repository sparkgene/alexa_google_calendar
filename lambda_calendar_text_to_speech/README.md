# lambda_calendar_text_to_speech
convert japanese text to audio.
This use  IBM Text to Speech service.
https://www.ibm.com/watson/developercloud/doc/text-to-speech/

## configuration

### WATSON_USER_NAME, WATSON_PASSWORD

IBM Text to Speech service credentials

### AUDIO_BUCKET

S3 audio bucket


## Installation

```
cd lambda_calendar_text_to_speech
pip install -r requirements.txt -t $(pwd)
```

compress all files in to zip.
```
zip -r func.zip .
```

upload to lambda function

This function use long time to convert data.
Set the timeout to 5 minuets.
