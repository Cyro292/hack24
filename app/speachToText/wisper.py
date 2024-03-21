import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


async def transcripeAudioFileToText(audio_file_path: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = "Transcribe the following audio to text:"

    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, prompt=prompt
        )
    return transcription["text"]
