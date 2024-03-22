import json
from .open_ai import get_ai_awnser_with_function


def get_reroute_info(question: str):

    with open("data/json/contact_info.json") as f:
        router = json.load(f)

    prompt = f"Du bist eine Callcenter AI und hast einen Anruf von einem Kunden bezüglich St. Gallen. Der Kunde hat nun folgende Frage gestellt {question} \n \n {router} \n\n"
    function_data = [
        {
            "name": "reroute",
            "description": "Verwende ausschließlich die Informationen, die du in der Frage und in den Kontakten hast. Sei schnell",
            "parameters": {
                "type": "object",
                "properties": {
                    "reroute_number": {
                        "type": "number",
                        "description": "Did the user specifically indicate that they want to speak with a specific human person? If not, they did NOT indicate it, the value shoud be 0. If they specifically indicated it, give 10. ",
                    },
                    "department": {
                        "type": "string",
                        "description": "abteilung an die der Anruf weitergeleitet werden soll.",
                    },
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

    response = get_ai_awnser_with_function(
        question, prompt, function_data, tool_choice=tool_choice
    )

    content = response.choices[0].message
    arguments = json.loads(content.tool_calls[0].function.arguments)
    reroute_number = arguments["reroute_number"]
    telephone_number = arguments["telephone_number"]
    department = arguments["department"]

    return arguments
