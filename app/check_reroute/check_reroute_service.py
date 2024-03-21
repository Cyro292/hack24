import json
from .open_ai import get_ai_awnser_with_function


async def get_reroute_info(question: str):

    with open("data/json/contact_info.json") as f:
        router = json.load(f)

    prompt = f"Du bist eine Callcenter AI und hast einen Anruf von einem Kunden bezüglich St. Gallen. Der Kunde hat nun folgende Frage gestellt {question} \n \n Schlage ihm eine der Folgenden Kontakte vor {router} \n\n"
    function_data = [
        {
            "name": "reroute",
            "description": "Verwende ausschließlich die Informationen, die du in der Frage und in den Kontakten hast. Sei schnell",
            "parameters": {
                "type": "object",
                "properties": {
                    "reroute_number": {
                        "type": "number",
                        "description": "Gib werte von 1 bis 10. 0 bedeutet er will mit der AI weitersprechen und nicht weiterleitet werden. 10 bedeutet der Kunde will unbedingt zu einem Menschlichen Mitarbeiter weiterleiten.",
                    },
                    "department": {"type": "string", "description": "abteilung"},
                    "telephone_number": {
                        "type": "string",
                        "description": "Telephone Number to call",
                    },
                },
                "required": ["reroute_number", "department", "telephone_number"],
            },
        }
    ]

    tool_choice = {"type": "function", "function": {"name": "reroute"}}

    response = await get_ai_awnser_with_function(
        question, prompt, function_data, tool_choice=tool_choice
    )

    content = response.choices[0].message
    arguments = json.loads(content.tool_calls[0].function.arguments)
    reroute_number = arguments["reroute_number"]
    telephone_number = arguments["telephone_number"]
    department = arguments["department"]

    return arguments
