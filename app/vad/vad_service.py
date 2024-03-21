from .picovoice import possibility_of_speech

FRAME_LENGTH = 512


async def get_possibility_of_speech(audio_data: bytes) -> float:
    """
    Returns the probability of speech in the audio data.
    """
    # Split the audio data into frames of length FRAME_LENGTH
    frames = [
        audio_data[i : i + FRAME_LENGTH]
        for i in range(0, len(audio_data), FRAME_LENGTH)
    ]

    # Process each frame and average the results
    results = [
        possibility_of_speech(frame)
        for frame in frames
        if len(frame) == FRAME_LENGTH
    ]
    return sum(results) / len(results) if results else 0


async def is_speech(audio_data: bytes) -> bool:
    """
    Returns True if speech is detected in the audio data.
    """
    return await get_possibility_of_speech(audio_data) > 0.1
