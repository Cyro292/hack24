import webrtcvad


def is_speech(byte_data, sample_rate=16000, padding_duration_ms=30, mode=2):
    """
    Analyzes a byte stream of audio to determine if it is speech or not.

    Parameters:
        byte_data: The byte stream of audio data.
        sample_rate: The audio sample rate. WebRTC VAD supports 8000, 16000, 32000, and 48000.
        padding_duration_ms: The duration of padding in milliseconds. This affects sensitivity.
        mode: An integer between 0 and 3. 0 is the least aggressive about filtering out non-speech, 3 is the most aggressive.

    Returns:
        A boolean indicating if speech was detected in the audio.
    """
    vad = webrtcvad.Vad(mode)

    # Calculate the number of padding frames.
    frame_duration_ms = 10  # Duration of a frame.
    frames = byte_data_to_frames(byte_data, sample_rate, frame_duration_ms)
    num_padding_frames = padding_duration_ms // frame_duration_ms

    # Add padding frames to the start and end of the frames list.
    frames = (
        [b"\x00" * (sample_rate * frame_duration_ms // 1000 * 2)] * num_padding_frames
        + frames
        + [b"\x00" * (sample_rate * frame_duration_ms // 1000 * 2)] * num_padding_frames
    )

    # Check if any frame within the byte stream contains speech.
    for frame in frames:
        if vad.is_speech(frame, sample_rate):
            return True
    return False


def byte_data_to_frames(byte_data, sample_rate, frame_duration_ms):
    """
    Converts byte data to a list of frames suitable for analysis with WebRTC VAD.

    Parameters:
        byte_data: The byte stream of audio data.
        sample_rate: The audio sample rate.
        frame_duration_ms: The duration of each frame in milliseconds.

    Returns:
        A list of byte frames.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    frames = []
    while offset + n < len(byte_data):
        frames.append(byte_data[offset : offset + n])
        offset += n
    return frames
