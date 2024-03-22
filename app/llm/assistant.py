import time
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class Assistant:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    id = 'asst_lDEntqOlH9CL6J7QKcdDgl3Q'
    thread = None
    run = None

    def __init__(self):
        pass

    def ask(self, question: str):
        if self.thread:
            self.__add_msg_to_thread(question)
        else:
            self.__create_thread(question)
        self.__run()

    def __create_thread(self, question: str):
        self.thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ]
        )

    def __add_msg_to_thread(self, question: str):
        self.client.beta.threads.messages.create(
            self.thread.id,
            role="user",
            content=question,
        )

    def __run(self):
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.id
        )

    def get_answer(self) -> str:
        print('status: ', self.run.status)
        if self.run.status != 'completed':
            time.sleep(1)
            try:
                self.run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=self.run.id
                )
            except Exception as e:
                print(e)
            return self.get_answer()
        else:
            thread_messages = self.client.beta.threads.messages.list(
                self.thread.id)
            content = [
                c for c in thread_messages.data[0].content if c.type == 'text'
            ]
            return content[0].text.value

    def get_user_message_history(self) -> list:
        users = ['Kanton St Gallen', 'Anrufer']
        print("Retrieving msg history")
        thread_messages = self.client.beta.threads.messages.list(
            self.thread.id)

        msg_texts = []
        for (i, msg) in enumerate(thread_messages.data[0].content):
            if (msg.type == 'text'):
                msg_texts.append({users[i % 2]: msg.text.value})

        return msg_texts

    def summarize_msg_history(self) -> str:
        msg_history = self.get_user_message_history()
        print("Summarizing msg history")

        summary = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Erstelle eine Zusammenfassung der Nachrichtenhistorie zwischen dem Anrufer und \"Kanton St Gallen\". Die Zusammenfassung soll aus Sicht des Anrufers sein."},
                {"role": "user", "content": json.dumps(msg_history)}
            ]
        )

        print('Finished summarizing msg history')

        return summary.choices[0].message.content[0].text.value
