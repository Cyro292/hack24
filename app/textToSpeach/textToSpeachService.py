from .polly import requestPollyFromText


async def getAudioLinkFromText(text: str):
    response = await requestPollyFromText(text)
    link: str = response["SynthesisTask"]["OutputUri"]
    return link

