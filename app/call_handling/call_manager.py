import os
from fastapi import FastAPI, WebSocket, Response, HTTPException, Request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from dotenv import load_dotenv
from app.text_to_speech.text_to_speech_service import (
    create_audio_file_from_text,
)
import time

load_dotenv()


class Call:

    STATES = {
        "INITIAL": 0,
        "LISTENING": 1,
        "SPEAKING": 2,
        "REROUTE": 3,
        "PROCESSING": 4,
        "END": 5,
    }

    def __init__(self) -> None:
        account_sid = "AC690145ec38222226d949960846d71393"
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        client = Client(account_sid, auth_token)
        state = self.STATES["INITIAL"]

    def twiml(self, resp):
        return Response(content=str(resp), media_type="text/xml")

    def make_call(self):
        call = self.client.calls.create(
            url="http://demo.twilio.com/docs/voice.xml",
            to="+41779671592",
            from_="+14243651541",
        )

        print(call.sid)

    async def send_welcome_message(self, request: Request):
        resp = VoiceResponse()

        # Play an audio file for the caller
        ## say welcome to the City of St.Gallen support service. We are here to help you. Please tell us how we can help you today?
        message = "Hallo und Willkommen bei der Stadt St.Gallen. Wir sind hier um Ihnen zu helfen. Bitte sagen Sie uns, wie wir Ihnen heute helfen können."

        timestamp = time.time()
        audio_filename = f"output_{timestamp}.mp3"

        await create_audio_file_from_text(
            message,
            f"assets/audio/{audio_filename}",
        )

        audio_filelink = f"{request.base_url}audio/{audio_filename}"
        resp.play(audio_filelink)

        # Redirect to a custom URL
        next_url = f"{request.base_url}voice/next"
        resp.redirect(next_url)

        self.state = self.STATES["LISTENING"]

        return self.twiml(resp)

    async def send_message(self, request: Request, message: str):
        resp = VoiceResponse()

        timestamp = time.time()
        audio_filename = f"output_{timestamp}.mp3"

        await create_audio_file_from_text(
            message,
            f"assets/audio/{audio_filename}",
        )

        audio_filelink = f"{request.base_url}audio/{audio_filename}"
        resp.play(audio_filelink)

        return self.twiml(resp)

    async def send_reply(self, request, path):
        print("path:  ", path)
        if path == "welcome":
            print("Welcome")
            self.state = self.STATES["INITIAL"]
            return await self.send_welcome_message(request)
        elif path == "next":
            print("Next")
            return await self.send_message(request, "Ich höre")
        else:
            raise HTTPException(status_code=404, detail="Path not found")
