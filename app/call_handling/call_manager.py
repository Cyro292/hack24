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
    def __init__(self) -> None:
        account_sid = "AC690145ec38222226d949960846d71393"
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        client = Client(account_sid, auth_token)

    def twiml(self, resp):
        return Response(content=str(resp), media_type="text/xml")

    def make_call(self):
        call = self.client.calls.create(
            url="http://demo.twilio.com/docs/voice.xml",
            to="+41779671592",
            from_="+14243651541",
        )

        print(call.sid)

    async def send_reply(self, request, path):
        """Respond to incoming phone calls with a 'Hello world' message"""
        # Start our TwiML response
        resp = VoiceResponse()

        # Read a message aloud to the caller
        # resp.say("Hello world!")

        # Play an audio file for the caller
        timestamp = time.time()
        audio_filename = f"output_{timestamp}.mp3"
        await create_audio_file_from_text(
            "Hallo Welt. Ich bin dein Sprachassistent.",
            f"assets/audio/{audio_filename}",
        )
        audio_filelink = f"{request.base_url}audio/{audio_filename}"
        resp.play(audio_filelink)

        # Convert the response to a string and set the content type to 'text/xml'
        return self.twiml(resp)
