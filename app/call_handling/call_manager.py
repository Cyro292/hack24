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
    
    
    call_number = None
    client = None
    state = None
    assistant = None
    prev_statement = ""
    TIMEOUT_FOR_LISTENING = 3

    def __init__(self, call_number) -> None:
        account_sid = "AC690145ec38222226d949960846d71393"
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        self.client = Client(account_sid, auth_token)
        self.state = self.STATES["INITIAL"]
        self.assistant = Assistant()
        self.call_number = call_number

    def twiml(self, resp):
        return Response(content=str(resp), media_type="text/xml")

    async def send_sms(self, body: str, to: str):
        if to is None:
            to = self.call_number
            
        message = self.client.messages.create(
            from_="+14243651541", body=body, to=to)

        print(message.sid)

        return message.sid

    async def redirect_call(self, request: Request, message: str, phone_no: str):
        resp = VoiceResponse()

        # message = "Ich verbinde Sie gleich mit einem Kollegen, der optimal auf Ihre Frage eingehen kann. Bitte haben Sie einen kurzen Moment Geduld."
        # "Ich leite Ihren Anruf an den nächsten verfügbaren Agenten weiter. Bitte warten Sie einen Moment."

        timestamp = time.time()
        audio_filename = f"output_{timestamp}.mp3"

        await create_audio_file_from_text(
            message, f"assets/audio/{audio_filename}"
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

        # say welcome to the City of St.Gallen support service. We are here to help you. Please tell us how we can help you today?
        # message = "Hallo und Willkommen bei der Stadt St.Gallen. Wir sind hier um Ihnen zu helfen. Bitte sagen Sie uns, wie wir Ihnen heute helfen können."
        message = "Herzlich willkommen bei der Info-Nummer des Kantons St. Gallen! Wir freuen uns sehr, Sie bei uns zu haben. Bitte sagen Sie uns, wie wir Ihnen heute helfen können."

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

    async def send_message(
        self,
        request: Request,
        message: str,
        next_url=None,
        voice_profile="de-At/Hannah",
    ):
        resp = VoiceResponse()

        timestamp = time.time()
        audio_filename = f"output_{timestamp}.mp3"

        await create_audio_file_from_text(
            message, f"assets/audio/{audio_filename}", voice_profile
        )

        audio_filelink = f"{request.base_url}audio/{audio_filename}"
        resp.play(audio_filelink)

        if next_url:
            resp.redirect(next_url)

        return self.twiml(resp)

    async def end_call(self, request: Request):
        resp = VoiceResponse()

        message = "Vielen Dank für Ihren Anruf.Zögern Sie nicht, die Info-Nummer erneut anzurufen, falls weitere Fragen auftauchen. Eine Zusammenfassung Ihrer Frage sowie die erteilten Ratschläge und Ressourcen erhalten Sie per SMS. Einen schönen Tag noch und auf Wiedersehen!"
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
            timeout=self.TIMEOUT_FOR_LISTENING,
            action=f"{request.base_url}voice/respond",
            method="POST",
            language="de-DE",
        )

        resp.append(gather)

        # Start recording the call and set the callback URL
        record = Record(
            recordingStatusCallback=f"{request.base_url}voice/recording",
            timeout=10,
            playBeep=False,
            trim="trim-silence",
            recordingStatusCallbackMethod="POST",
            recordingStatusCallbackEvent="completed",
        )
        resp.append(record)

        return self.twiml(resp)

    async def handle_recording(self, request: Request):
        data = await request.form()
        recording_url = data.get("RecordingUrl")

        if recording_url is None:
            print("No recording URL received.")
        else:
            recording_url = f"{recording_url}.mp3"
            print("Recording URL: ", recording_url)
            # download the file from recording_url and save the recording to assets/audio folder
            timestamp = time.time()

        return {"status": "success"}

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

            self.speech_result = data.get("SpeechResult")
            if self.speech_result is None:
                print("SpeechResult is not available.")
            else:
                print("SpeechResult: ", self.speech_result)

            confidence = data.get("Confidence")
            if confidence is None:
                confidence = 0
                print("Confidence is not available.")
            else:
                print("Confidence: ", confidence, type(confidence))
                print("Confidence: ", float(confidence), type(float(confidence)))
                confidence = float(confidence)

            language = data.get("Language")
            if language is None:
                print("Language is not available.")
            else:
                print("Language: ", language)

            if language != "de-DE":
                self.state = self.STATES["SPEAKING"]
                return await self.send_message(
                    request,
                    "Hi! The Kanton of St. Gallen's information number only supports German for now. Please ask your questions in German. Thank you for your understanding!",
                    next_url=f"{request.base_url}voice/listen",
                    voice_profile="en-GB/Arthur",
                )
            elif confidence < 0:
                self.state = self.STATES["SPEAKING"]
                return await self.send_message(
                    request,
                    "Ich konnte Sie leider nicht verstehen. Könnten Sie Ihre Anfrage bitte wiederholen?",
                    next_url=f"{request.base_url}voice/listen",
                )
            else:
                self.state = self.STATES["PROCESSING"]

                self.assistant.ask(self.speech_result)

                return await self.send_message(
                    request,
                    "Ich habe verstanden bitte warten Sie einen Moment.",
                    next_url=f"{request.base_url}voice/process",
                )

        elif path == "process":
            print("Process")

            # call the assistant and the router
            answer, reroute_n, tel_n, department = call_llms(
                self.assistant, self.speech_result, self.prev_statement
            )

            self.prev_statement = answer

            print("Reroute number: ", reroute_n)

            if int(reroute_n) == 10:
                department: str = department.replace("_", " ")
                message = f"Ich verbinde Sie gleich mit einem Kollegen der Abteilung {department}. Bitte haben Sie einen kurzen Moment Geduld."
                return await self.redirect_call(request, message, "+41772800638")
            else:
                print("Answer: ", answer)
                return await self.send_message(
                    request, answer, next_url=f"{request.base_url}voice/listen"
                )

        elif path == "recording":
            print("Recording")
            await self.handle_recording(request)

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


def router_task(question: str, prev_statement: str):
    return get_reroute_info(question, prev_statement)


def call_llms(assistant: Assistant, question: str, prev_statement: str):
    results = []

    # Call the router + assistant concurrently to reduce IO-bound latency
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(assistant_task, assistant),
            executor.submit(router_task, question, prev_statement),
        ]

        results = [future.result() for future in futures]

    return (
        results[0],
        results[1]["reroute_number"],
        results[1]["telephone_number"],
        results[1]["department"],
    )


def reroute(reroute_n: int) -> bool:
    return reroute_n > 6
