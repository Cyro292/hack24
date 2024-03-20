import os
import boto3
import asyncio
from contextlib import closing
from dotenv import load_dotenv


load_dotenv()


async def requestPollyFromText(text: str):

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
