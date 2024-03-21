from fastapi import FastAPI
from app.textToSpeach.textToSpeachService import getAudioLinkFromText, createAudioFileFromText

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/polly/")
async def polly():

    response = await createAudioFileFromText("Hallo Welt. Ich bin dein Sprachassistent.", "assets/audio/output.mp3")

    return {
        "link": response,
    }
    
@app.get('/wisper/')
async def wisper():
    
    
    
    return {"message": "Not implemented yet."}