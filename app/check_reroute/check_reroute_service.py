import json
from .open_ai import get_ai_answer_with_function


def get_reroute_info(answer_customer: str, prev_statement: str):

    with open("data/json/contact_info.json") as f:
        router = json.load(f)

    prompt = f"Du bist ein Mitarbeiter im Callcenter vom Schweizer Kanton \"St. Gallen\". Deine Vorherige Aussage war folgende:\n\"\"\"{prev_statement}\"\"\"Ein Kunde antwortet:\n\"\"\"{answer_customer}\"\"\"\n\n."
    function_data = [
        {
            "name": "reroute",
            "description": "Verwende ausschließlich die Informationen, die du aus dem Kundengespräch hast.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reroute_number": {
                        "type": "number",
                        "description": "Gibt eine Zahl zwischen 0 und 10 zurück. Gibt 10 zurück, wenn der Benutzer ausdrücklich darum gebeten hat, mit einem bestimmten Mitarbeiter zu sprechen. Andernfalls wird 0 zurückgegeben. Wenn der Anrufer deutlich zu verstehen gibt, dass er das Gespräch beenden möchte, indem er z. B. sagt: Danke für den Anruf, tschüss oder Mir geht es gut, danke oder Ich werde/will jetzt auflegen, rufen Sie bitte die 15 zurück.",
                    },
                    "department": {
                        "type": "string",
                        "description": "Gibt die Abteilung zurück, an die der Anruf weitergeleitet werden soll.",
                    },
                    "telephone_number": {
                        "type": "string",
                        "description": "Gibt die Telefonnummer zurück, an die der Anruf weitergeleitet werden soll.",
                    },
                },
                "required": ["reroute_number", "department", "telephone_number"],
            },
        }
    ]

    tool_choice = {"type": "function", "function": {"name": "reroute"}}

    response = get_ai_answer_with_function(
        answer_customer, prompt, function_data, tool_choice=tool_choice
    )

    content = response.choices[0].message
    arguments = json.loads(content.tool_calls[0].function.arguments)
    reroute_number = arguments["reroute_number"]
    telephone_number = arguments["telephone_number"]
    department = arguments["department"]

    return arguments
