import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


async def get_reroute_response_from_question(question: str, contexts: list[str]):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    context = "\n".join(contexts)
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Gebe den Wert \"reroute\" zurück. Dieser Value liegt zwischen 0 und 1 und gibt an, wie relevant der Kontext zur gestellten Frage ist. Wenn der Kontext irrelevant ist, soll \"reroute\" nahe an 0 sein. Wenn der Kontext sehr relevant ist soll \"reroute\" nahe an 1 sein. Kontext:\n\"\"\"{context}\"\"\"\n\n",
            },
            {"role": "user", "content": f'Frage:\n\"\"\"{question}\"\"\"'},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    return response
