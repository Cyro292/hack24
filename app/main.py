from fastapi import FastAPI, WebSocket, HTTPException, Request
from fastapi.responses import FileResponse
from app.text_to_speech.text_to_speech_service import (
    create_audio_file_from_text,
)
from app.speech_to_text.speech_to_text_service import get_text_from_audio_file
from app.check_reroute.check_reroute_service import get_reroute_nessary
from app.vad.webrtc_service import is_speech
from app.check_reroute.check_reroute_service import get_reroute_nessary 
import os
from app.call_handling.call_manager import Call

app = FastAPI()

call = Call()


@app.get("/")
async def root():
    return {"message": "Hello World v1.2.1"}


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
        "Biite leite mich zu Migrationsamt weiter",
        "-",
    )

    return {"message": response}


@app.websocket("/word_probability/")
async def word_probability(websocket: WebSocket):
    await websocket.accept()
    while True:
        audio_data = await websocket.receive_bytes()
        speech_probability = is_speech(audio_data)
        await websocket.send_text(f"Speech probability: {speech_probability}")


@app.post("/voice/{path:path}")
async def voice(request: Request, path: str):
    print("voice request", request)
    return await call.send_reply(request, path)


@app.get("/audio/{name}")
async def get_audio(name: str):
    """Retrieve an audio file by its name"""
    file_path = f"assets/audio/{name}"
    print("file_path", file_path)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(file_path, media_type="audio/mpeg")


@app.get("/redirect_nessar/")
async def redirect_nessar():
    return {"message": "Hello World v1.2.1"}
