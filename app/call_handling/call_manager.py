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
from app.llm.assistant import Assistant
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.check_reroute.check_reroute_service import get_reroute_info

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
        assistant = Assistant()

    def twiml(self, resp):
        return Response(content=str(resp), media_type="text/xml")

    async def redirect_call(self, request: Request, phone_no: str):
        resp = VoiceResponse()

        message = "Ich leite Ihren Anruf an den nächsten verfügbaren Agenten weiter. Bitte warten Sie einen Moment."

        timestamp = time.time()
        audio_filename = f"output_{timestamp}.mp3"

        await create_audio_file_from_text(
            message,
            f"assets/audio/{audio_filename}",
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
        # say welcome to the City of St.Gallen support service. We are here to help you. Please tell us how we can help you today?
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
                print("Confidence: ", float(confidence),
                      type(float(confidence)))
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

                self.assistent.ask(speech_result)

                return await self.send_message(request, "Ich habe verstanden bitte warten Sie einen Moment.", next_url=f"{request.base_url}voice/process")

        elif path == "process":
            print("Process")

            # call the assistant and the router
            answer, reroute_n, tel_n, department = call_llms(
                self.assistent, speech_result)

            if int(reroute_n) > 6:
                print(tel_n, department)
                return await self.redirect_call(request, "+41772800638")
            else:
                return await self.send_message(request, answer, next_url=f"{request.base_url}voice/listen")
        elif path == "next":
            print("Next")
            return await self.send_message(request, "Ich höre")
        elif path == "end":
            print("End")
            return await self.end_call(request)
        else:
            raise HTTPException(status_code=404, detail="Path not found")


def assistant_task(instance: Assistant):
    return instance.get_answer()


def router_task(question: str):
    return get_reroute_info(question)


def call_llms(assistant: Assistant, question: str):
    # Call the router + assistant concurrently to reduce IO-bound latency
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(
            assistant_task, assistant), executor.submit(router_task, question)]

    results = []

    for future in as_completed(futures):
        try:
            result = future.result()
            results.append(result)
        except Exception as e:
            print("Exception: ", e)

    answer = results[0]
    reroute_n, tel_n, department = results[1]

    return answer, reroute_n, tel_n, department


def reroute(reroute_n: int) -> bool:
    return reroute_n > 6
