from .wisper import transcripeAudioFileToText


async def getResponseFromAudioFile(audio_file_path: str):
    return transcripeAudioFileToText(audio_file_path=audio_file_path)


async def getTextFromAudioFile(audio_file_path: str):
    response = await transcripeAudioFileToText(audio_file_path)
    return response.text
