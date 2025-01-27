from openai import OpenAI
from supabase_utils import log_message_to_supabase

client = OpenAI()

def transcribe_audio_file(audio_file, session_id: str) -> str:
    """
    Transcribe audio using OpenAI Whisper API.
    
    Args:
        audio_file: Audio file object from Streamlit's file_uploader
        session_id (str): Session ID for logging
    
    Returns:
        str: Transcribed text
    """
    try:
        # Transcribe using Whisper
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        
        # Log successful transcription
        log_message_to_supabase(
            session_id=session_id,
            message_type="system",
            content="Audio transcribed successfully",
            metadata={"transcription": transcript.text}
        )
        
        return transcript.text
        
    except Exception as e:
        error_message = f"Error transcribing audio: {str(e)}"
        # Log error
        log_message_to_supabase(
            session_id=session_id,
            message_type="error",
            content=error_message
        )
        raise Exception(error_message)
