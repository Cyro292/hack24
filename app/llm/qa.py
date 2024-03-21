import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_answer_to_caller_question_from_llm(question: str, contexts: list[str]) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model='gpt-4-turbo',
        messages=[
            {
                "role": "system",
                "content": 'Dir wird eine Frage gestellt die du freundlich aber so kurz wie möglich beantworten musst. Zusätzlich zu der Frage wirst du 3 Kontexte bekommen, welcher nützliche Informationen enthalten die du benutzen kannst. Die Kontexte sind nach Priorität sortiert (1 ist die höchste Priorität und 3 die niedrigste).',
            },
            {"role": "user", "content": format_content(question, contexts)},
        ],
        temperature=0.3
    )
    return response.choices[0].message["content"]


def format_content(question: str, contexts: list[str]) -> str:
    questionPart = f'Frage:\n\"\"\"\n{question}\n\n\n'
    contextPart = ''
    for i, c in contexts:
        contextPart += format_context(c, i)

    def format_context(context: str, idx: int) -> str:
        return f'Kontext (Priorität {3-idx}):\n\"\"\"\n{context}\n\"\"\"\n\n'

    return questionPart + contextPart
