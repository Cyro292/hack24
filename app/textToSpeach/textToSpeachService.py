import httpx
from .polly import requestPollyFromText


async def getResponseFromText(text: str):
    response = await requestPollyFromText(text)
    return response


async def getAudioLinkFromText(text: str):
    response = await requestPollyFromText(text)
    link: str = response["SynthesisTask"]["OutputUri"]
    return link


async def createAudioFileFromText(text: str, output_path):
    response = await requestPollyFromText(text)
    link: str = response["SynthesisTask"]["OutputUri"]

    try:
        async with httpx.AsyncClient(headers={"User-Agent": "myapp/0.0.1"}) as client:
            r = await client.get(link)
            r.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(r.content)
    except Exception as e:
        print(e)
        return link

    return link
