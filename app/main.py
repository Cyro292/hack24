from fastapi import FastAPI, Response
from app.text_to_speech.text_to_speech_service import (
    get_audio_link_from_text,
    create_audio_file_from_text,
)
from app.speech_to_text.speech_to_text_service import get_text_from_audio_file
from twilio.twiml.voice_response import VoiceResponse

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World v1.2.1"}


@app.get("/polly/")
async def polly():

    response = await create_audio_file_from_text(
        "Hallo Welt. Ich bin dein Sprachassistent.", "assets/audio/output.mp3"
    )

    return {
        "link": response,
    }


@app.get("/wisper/")
async def wisper():

    text = await get_text_from_audio_file("assets/audio/input.mp3")

    return {"transscript": {text}}


@app.get("/check-router/")
async def checkRedirect():
    return {"message": "Hello World"}




@app.post("/voice")
async def voice():
    """Respond to incoming phone calls with a 'Hello world' message"""
    # Start our TwiML response
    resp = VoiceResponse()

    # Read a message aloud to the caller
    # resp.say("Hello world!")
    
    # Play an audio file for the caller
    link = await create_audio_file_from_text(
        "Hallo Welt. Ich bin dein Sprachassistent.", "assets/audio/output.mp3"
    )
    resp.play(link)

    # Convert the response to a string and set the content type to 'text/xml'
    return Response(content=str(resp), media_type="text/xml")
