# lambda_calendar_text_to_speech_polly
convert japanese text to audio.
This use Amazon Polly to create audio data.
https://aws.amazon.com/polly/

## Installation

```
cd lambda_calendar_text_to_speech_polly
pip install -r requirements.txt -t $(pwd)
```

compress all files in to zip.
```
zip -r func.zip .
```

upload to lambda function

This function use long time to convert data.
Set the timeout to 5 minuets.
