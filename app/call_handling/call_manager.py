import os
from fastapi import FastAPI, WebSocket, Response, HTTPException, Request
from twilio.twiml.voice_response import VoiceResponse, Gather, Record, Dial
from twilio.rest import Client
from dotenv import load_dotenv
from app.text_to_speech.text_to_speech_service import (
    create_audio_file_from_text,
)
import time
import json

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
    
    client = None
    state = None

    def __init__(self) -> None:
        account_sid = "AC690145ec38222226d949960846d71393"
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        self.client = Client(account_sid, auth_token)
        self.state = self.STATES["INITIAL"]

    def twiml(self, resp):
        return Response(content=str(resp), media_type="text/xml")
      
    async def send_sms(self, body: str, to: str):
        message = self.client.messages.create(
            from_='+14243651541',
            body=body,
            to=to
        )

        print(message.sid)
        
        return message.sid

    async def redirect_call(self, request: Request, phone_no: str):
        resp = VoiceResponse()
        
        message = "Ich leite Ihren Anruf an den nächsten verfügbaren Agenten weiter. Bitte warten Sie einen Moment."

        timestamp = time.time()
        audio_filename = f"output_{timestamp}.mp3"

        await create_audio_file_from_text(
            message,
            f"assets/audio/{audio_filename}", voice_profile="de-DE/Daniel"
        )

        audio_filelink = f"{request.base_url}audio/{audio_filename}"
        resp.play(audio_filelink)
        
        # Dial the given phone number
        dial = Dial()
        dial.number(phone_no)
        resp.append(dial)

        return self.twiml(resp)

    async def send_welcome_message(self, request: Request):
        resp = VoiceResponse()

        # Play an audio file for the caller
        ## say welcome to the City of St.Gallen support service. We are here to help you. Please tell us how we can help you today?
        # message = "Hallo und Willkommen bei der Stadt St.Gallen. Wir sind hier um Ihnen zu helfen. Bitte sagen Sie uns, wie wir Ihnen heute helfen können."
        message = "Hallo und Willkommen bei der Stadt St.Gallen. Bitte sagen Sie uns, wie wir Ihnen heute helfen können."

        timestamp = time.time()
        audio_filename = f"output_{timestamp}.mp3"

        await create_audio_file_from_text(
            message,
            f"assets/audio/{audio_filename}",
        )

        audio_filelink = f"{request.base_url}audio/{audio_filename}"
        resp.play(audio_filelink)

        # Redirect to a custom URL
        next_url = f"{request.base_url}voice/listen"
        resp.redirect(next_url)

        return self.twiml(resp)

    async def send_message(self, request: Request, message: str, next_url=None):
        resp = VoiceResponse()

        timestamp = time.time()
        audio_filename = f"output_{timestamp}.mp3"

        await create_audio_file_from_text(
            message,
            f"assets/audio/{audio_filename}",
        )

        audio_filelink = f"{request.base_url}audio/{audio_filename}"
        resp.play(audio_filelink)

        if next_url:
            resp.redirect(next_url)

        return self.twiml(resp)

    async def end_call(self, request: Request):
        resp = VoiceResponse()

        message = "Vielen Dank für Ihren Anruf. Auf Wiedersehen."
        timestamp = time.time()
        audio_filename = f"output_{timestamp}.mp3"

        await create_audio_file_from_text(
            message,
            f"assets/audio/{audio_filename}",
        )

        audio_filelink = f"{request.base_url}audio/{audio_filename}"
        resp.play(audio_filelink)

        resp.hangup()

        return self.twiml(resp)

    async def listen_call(self, request: Request):
        resp = VoiceResponse()

        gather = Gather(
            input="speech",
            timeout=3,
            action=f"{request.base_url}voice/respond",
            method="POST",
            language="de-DE",
        )

        resp.append(gather)
        
        return self.twiml(resp)

    async def send_reply(self, request, path):
        print("path: ", path)
        if path == "welcome":
            print("Welcome")
            self.state = self.STATES["INITIAL"]
            return await self.send_welcome_message(request)
        elif path == "listen":
            print("Listen")
            self.state = self.STATES["LISTENING"]
            return await self.listen_call(request)
        elif path == "respond":
            print("Respond")
            self.state = self.STATES["PROCESSING"]
            data = await request.form()
            
            # print("Data received in action callback: ", data)
            
            speech_result = data.get('SpeechResult')
            if speech_result is None:
                print("SpeechResult is not available.")
            else:
                print("SpeechResult: ", speech_result)

            confidence = data.get('Confidence')
            if confidence is None:
                confidence = 0
                print("Confidence is not available.")
            else:
                print("Confidence: ", confidence, type(confidence))
                print("Confidence: ", float(confidence), type(float(confidence)))
                confidence = float(confidence)

            language = data.get('Language')
            if language is None:
                print("Language is not available.")
            else:
                print("Language: ", language)
            
            if language != "de-DE":
                self.state = self.STATES["SPEAKING"]
                return await self.send_message(request, "Ich habe Sie nicht verstanden. Bitte sprechen Sie Deutsch.", next_url=f"{request.base_url}voice/listen")
            elif confidence < 0:
                self.state = self.STATES["SPEAKING"]
                return await self.send_message(request, "Ich habe Sie nicht verstanden. Bitte wiederholen Sie Ihre Anfrage.", next_url=f"{request.base_url}voice/listen")
            else:
                self.state = self.STATES["PROCESSING"]
                return await self.send_message(request, "Ich habe verstanden bitte warten Sie einen Moment.", next_url=f"{request.base_url}voice/process")

        elif path == "process":
            print("Process")
            ## TODO: Implement the processing logic here
            
            return await self.redirect_call(request, "+41772800638")
            
            
        elif path == "next":
            print("Next")
            return await self.send_message(request, "Ich höre")
        elif path == "end":
            print("End")
            return await self.end_call(request)
        else:
            raise HTTPException(status_code=404, detail="Path not found")
