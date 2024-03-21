from .speech_to_text.speech_to_text_service import get_text_from_audio_file
from .text_to_speech.text_to_speech_service import create_audio_file_from_text
from .check_reroute.check_reroute_service import get_reroute_nessary

async def audio_to_audio(path_to_audio) -> str:
    
    transcript = get_text_from_audio_file(path_to_audio)
    transcript2 = get_text_from_audio_file(path_to_audio)
    
    processed = await transcript
    processed2 = await transcript2
    # TODO: process the transcript to get response
    
    reroute_nessary = get_reroute_nessary(processed, "-")
    

    
    asset_path = "assets/audio/output.mp3"
    
    create_audio_file_from_text(processed, asset_path)
    
    #TODO: return the response
    
    
    
