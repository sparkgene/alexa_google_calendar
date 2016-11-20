# lambda_calendar_audio_transform
Convert audio data to Alexa required format.
https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/speech-synthesis-markup-language-ssml-reference#audio

## configuration

set these Environment variables on lambda function.

### PUBLIC_BUCKET

S3 bucket which contains transformed audio file.

## Installation

```
cd lambda_audio_transform
curl -L -O https://github.com/imageio/imageio-binaries/raw/master/ffmpeg/ffmpeg.linux64
```

compress all files in to zip.
```
zip -r func.zip .
```

This function use long time to convert data.
Set the timeout to 5 minuets.

Create a S3 trigger. Invoke when the object created.
