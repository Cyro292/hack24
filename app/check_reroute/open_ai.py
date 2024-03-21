import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


async def get_reroute_response_from_question(question: str, context: str):

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": f"{context} \n \n Gebe den value reroute zurück. Dieser Value liegt zwischen 0 und 1 und gibt an, ob ein reroute notwendig ist basierend darauf ob die Frage gut genug beantwortet wurde oder der nutzer nach einem menschlichen experten fragt.",
            },
            {"role": "user", "content": question},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    return response
