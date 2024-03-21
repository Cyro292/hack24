import pvcobra
import os
from dotenv import load_dotenv

load_dotenv()

def possibility_of_speech(audio_data: bytes) -> float:
    """
    Returns the probability of speech in the audio data.
    """
    client = pvcobra.create(access_key=os.getenv("PICOVOICE_AI_API_KEY"))
    processed = client.process(audio_data)
    return processed