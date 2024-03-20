from fastapi import FastAPI
from app.textToSpeach.textToSpeachService import getAudioLinkFromText

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/polly/")
async def polly():

    response = await getAudioLinkFromText("Hallo Welt. Ich bin dein Sprachassistent.")

    return {
        "link": response,
    }
