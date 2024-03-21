import json
from .open_ai import get_ai_awnser_with_function
from .router import router


async def get_reroute_nessary(question: str, context: str):

    prompt = f"Du bist eine Callcenter AI und hast einen Anruf von einem Kunden bezüglich St. Gallen. Der Kunde hat nun folgende Frage gestellt {context} \n \n Schlage ihm eine der Folgenden Kontakte vor {router} \n\n"
    function_data = [
        {
            "name": "reroute",
            "description": "Verwende ausschließlich die Informationen, die du in der Frage und in den Kontakten hast, um den Anruf an die richtige Abteilung weiterzuleiten. Sei schnell",
            "parameters": {
                "type": "object",
                "properties": {
                    "reroute_number": {"type": "number", "description": "Sichherit darüber ob der Anruf weitergeleitet werden soll oder nicht. 10 bedeutet weiterleiten, 0 bedeutet nicht weiterleiten"},
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

    response = await get_ai_awnser_with_function(question, prompt, function_data, tool_choice=tool_choice)

    content = response.choices[0].message
    arguments = json.loads(content.tool_calls[0].function.arguments)
    reroute_number = arguments["reroute_number"]
    telephone_number = arguments["telephone_number"]
    department = arguments["department"]

    return content
