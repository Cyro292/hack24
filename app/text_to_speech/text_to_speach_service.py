import httpx
from .polly import request_polly_from_text


async def get_response_from_text(text: str):
    response = await request_polly_from_text(text)
    return response


async def get_audio_link_from_text(text: str):
    response = await request_polly_from_text(text)
    link: str = response["SynthesisTask"]["OutputUri"]
    return link


async def create_audio_file_from_text(text: str, output_path):
    response = await request_polly_from_text(text)
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
