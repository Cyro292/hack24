from fastapi import FastAPI
from app.textToSpeach.text_to_speach_service import (
    getAudioLinkFromText,
    createAudioFileFromText,
)
from app.speach_to_text.speach_to_text_service import getTextFromAudioFile

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/polly/")
async def polly():

    response = await createAudioFileFromText(
        "Hallo Welt. Ich bin dein Sprachassistent.", "assets/audio/output.mp3"
    )

    return {
        "link": response,
    }


@app.get("/wisper/")
async def wisper():

    text = await getTextFromAudioFile("assets/audio/input.mp3")

    return {"transscript": {text}}


@app.get("/check-router/")
async def checkRedirect():
    return {"message": "Hello World"}
