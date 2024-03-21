from fastapi import FastAPI
from app.textToSpeach.textToSpeachService import (
    getAudioLinkFromText,
    createAudioFileFromText,
)
from app.speachToText.speachToTextService import getTextFromAudioFile

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

    return {"message": {text}}
