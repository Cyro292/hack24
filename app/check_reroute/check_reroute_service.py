from .open_ai import get_reroute_response_from_question


async def get_reroute_nessary(question: str):
    response = await get_reroute_response_from_question(question)
    
    content = response.choices[0].message["content"]
    
    if not content['reroute']:
        print("Something went wrong with the reroute")
        return False
    
    if content['reroute'] > 0.5:
        return True
    
    return False
