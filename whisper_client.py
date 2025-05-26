# Placeholder for Whisper transcription logic

import os
from openai import OpenAI

def validate_api_key(api_key):
    """Validate that the API key has a valid format."""
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
        
    valid_prefixes = ['sk-proj-', 'sk-None-', 'sk-svcacct-']
    if not any(api_key.startswith(prefix) for prefix in valid_prefixes):
        raise ValueError("Invalid OpenAI API key format")
    
    return True

def transcribe_audio(audio_path):
    """
    Transcribe an audio file using OpenAI's Whisper API.
    
    Args:
        audio_path (str): Path to the audio file (MP3 format)
        
    Returns:
        dict: Dictionary containing:
            - text (str): Full transcript text
            - segments (list): List of segments with timestamps
                - start (float): Start time in seconds
                - end (float): End time in seconds
                - text (str): Text for this segment
    """
    try:
        # Get and validate API key only when needed
        api_key = os.environ.get('OPENAI_API_KEY')
        validate_api_key(api_key)
        
        # Initialize client with validated key
        client = OpenAI(api_key=api_key)
        
        with open(audio_path, 'rb') as audio_file:
            # Call Whisper API with timestamps enabled
            response = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
            
            # Extract full text and segments
            result = {
                "text": response.text,
                "segments": [
                    {
                        "start": segment.start,
                        "end": segment.end,
                        "text": segment.text
                    }
                    for segment in response.segments
                ]
            }
            
            return result
            
    except Exception as e:
        raise Exception(f"Failed to transcribe audio: {str(e)}") 