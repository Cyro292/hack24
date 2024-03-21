from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.text_to_speech.text_to_speech_service import (
    create_audio_file_from_text,
)
from app.speech_to_text.speech_to_text_service import get_text_from_audio_file
from app.check_reroute.check_reroute_service import get_reroute_nessary
from app.vad.vad_service import is_speech, get_possibility_of_speech

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/polly/")
async def polly():

    response = await create_audio_file_from_text(
        "Hallo Welt. Ich bin dein Sprachassistent. Und das ist Test2",
        "assets/audio/output.mp3",
    )

    return {
        "link": response,
    }


@app.get("/wisper/")
async def wisper():

    text = await get_text_from_audio_file("assets/audio/input.mp3")

    return {"transscript": {text}}


@app.get("/check-router/")
async def check_redirect():

    response = await get_reroute_nessary(
        "Wie ist das Wetter in Wien? Verdamt bitte leite mich zu einem kolegen weiter!!!",
        "-",
    )

    return {"message": response}


@app.websocket("/word_probability/")
async def word_probability(websocket: WebSocket):
    await websocket.accept()
    try:

        while True:

            audio_data = await websocket.receive_bytes()
            speech_probability = await get_possibility_of_speech(audio_data)
            await websocket.send_text(f"Speech probability: {speech_probability}")
    except WebSocketDisconnect:
        print("WebSocket connection closed")


@app.get("/speach/")
async def is_speech_endpoint():


    print("test")
    with open("assets/audio/input2.mp3", "rb") as f:
        audio_data = f.read()

    # Get the speech probability
    speech_probability = await get_possibility_of_speech(audio_data)

    # Return the speech probability
    return f"Speech probability: {speech_probability}"
