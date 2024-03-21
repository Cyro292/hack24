import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


async def get_reroute_response_from_question(question: str):

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=os.getenv("REROUTE_OPENAI_MODEL"),
        messages=[
            {
                "role": "system",
                "content": "You need to decide if the reroute and need to decide with a number from 0 to 1 if the user wants a redirect to a human expert rather then the AI. 0 means no reroute and 1 means reroute. The var should be named reroute.",
            },
            {"role": "user", "content": question},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    return response
