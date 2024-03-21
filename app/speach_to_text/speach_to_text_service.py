from .wisper import transcripe_audio_file_to_text


async def get_response_from_audio_file(audio_file_path: str):
    return transcripe_audio_file_to_text(audio_file_path=audio_file_path)


async def get_text_from_audio_file(audio_file_path: str):
    response = await transcripe_audio_file_to_text(audio_file_path)
    return response.text
