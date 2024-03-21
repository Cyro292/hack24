from contextlib import closing
import os
import boto3
import asyncio
from dotenv import load_dotenv


load_dotenv()


async def request_polly_from_text(text: str):

    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    def start_speech_synthesis_task():
        client = session.client("polly")
        response = client.start_speech_synthesis_task(
            Engine="neural",
            LanguageCode="de-AT",
            OutputFormat="mp3",
            OutputS3BucketName=os.getenv("S3_BUCKET_NAME"),
            Text=text,
            VoiceId="Hannah",
        )
        return response

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, start_speech_synthesis_task)

    return response


async def audio_file_from_text(text: str, audio_output_path: str):

    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    def start_speech_synthesis_task():
        client = session.client("polly")
        response = client.synthesize_speech(
            Text=text,
            Engine="neural",
            LanguageCode="de-AT",
            OutputFormat="mp3",
            VoiceId="Hannah",
        )
        return response

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, start_speech_synthesis_task)

    with closing(response["AudioStream"]) as stream:
        with open(audio_output_path, "wb") as file:
            file.write(stream.read())

    return response
