import asyncio
import websockets
import pytest
import numpy as np
import soundfile as sf


@pytest.mark.asyncio
async def test_word_probability():
    uri = "ws://127.0.0.1:8000/word_probability/"
    async with websockets.connect(uri) as websocket:
        # Read the audio file
        data, samplerate = sf.read("assets/audio/input.mp3")

        # Calculate the number of samples per chunk
        chunk_duration = 1  # duration of each chunk in seconds
        samples_per_chunk = int(samplerate * chunk_duration)

        # Send the audio data in chunks
        for i in range(0, len(data), samples_per_chunk):
            chunk = data[i : i + samples_per_chunk]
            await websocket.send(chunk.tobytes())

            # Receive the response
            response = await websocket.recv()

            # Print the response
            print(f"Received: {response}")

            # Check that the response is as expected
            assert "Speech probability: " in response
