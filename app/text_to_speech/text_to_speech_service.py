import httpx
from .polly import request_polly_from_text, audio_file_from_text


async def get_response_from_text(text: str):
    response = await request_polly_from_text(text)
    return response


async def get_audio_link_from_text(text: str):
    response = await request_polly_from_text(text)
    link: str = response["SynthesisTask"]["OutputUri"]
    return link


async def create_audio_file_from_text(text: str, output_path: str, voice_profile: str = "de-At/Hannah"):
    response = await audio_file_from_text(text, output_path, voice_profile)
    return response
