from app.vad.webrtc import is_speech
import asyncio


async def get_is_speech_from_stream(stream: bytes):
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, is_speech, stream)
    return response
