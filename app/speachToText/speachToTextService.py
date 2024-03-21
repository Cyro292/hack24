from .wisper import transcripeAudioFileToText


async def audioFileToText(audio_file_path: str):
    return transcripeAudioFileToText(audio_file_path=audio_file_path)
