import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


async def ask_reroute(question: str):

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=os.getenv("REROUTE_OPENAI_MODEL"),
        messages=[
            {
                "role": "system",
                "content": "You are a Decider. You are in a conversation with a user who is asking for advice and you need find out if the user needs to be rerouted to a human expert. You should awnser in Json format. with the key reroute and the value true or false.",
            },
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message["content"]
