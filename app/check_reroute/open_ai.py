import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


async def get_ai_awnser(question: str, contexts: list[str]):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    context = "\n".join(contexts)
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": f"{context}\n\n",
            },
            {"role": "user", "content": f'Frage:\n"""{question}"""'},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    return response


def get_ai_awnser_with_function(
    question: str,
    contexts: list[str],
    function_data: list[dict],
    tool_choice=None,
):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    tools = [
        {"type": "function", "function": function_data[0]},
    ]

    context = "\n".join(contexts)
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": f"Du Gibst dabei immer im JSON Format deine Antwort zurück {context}\n\n",
            },
            {"role": "user", "content": f'Frage:\n"""{question}"""'},
        ],
        temperature=0.4,
        tools=tools,
        tool_choice=tool_choice,
        response_format={"type": "json_object"},
    )

    return response
