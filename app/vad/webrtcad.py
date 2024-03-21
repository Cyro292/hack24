import asyncio
import webrtcvad

vad = webrtcvad.Vad(3)  # Using a high aggressiveness mode.


def process_frame(frame, sample_rate=16000):
    """Synchronously checks if the given frame contains speech."""
    return vad.is_speech(frame, sample_rate)


async def is_speech_async(frame, sample_rate=16000):
    """Asynchronously checks if the given frame contains speech."""
    loop = asyncio.get_running_loop()
    # Run the synchronous VAD code in a threadpool executor to avoid blocking.
    return await loop.run_in_executor(None, process_frame, frame, sample_rate)
