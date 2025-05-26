"""
Box AI metadata formatter for structured metadata extraction.
"""
import json
from typing import Dict, List, Optional, Union

def create_metadata_template(template_key: str = "video_analysis") -> Dict:
    """
    Create a metadata template for video/audio analysis.
    
    Args:
        template_key (str): The key for the metadata template
        
    Returns:
        dict: A metadata template configuration
    """
    return {
        "type": "metadata_template",
        "scope": "enterprise",
        "template_key": template_key,
        "fields": [
            {
                "type": "string",
                "key": "transcript",
                "displayName": "Full Transcript",
                "description": "Complete transcript of the audio/video content"
            },
            {
                "type": "string",
                "key": "summary",
                "displayName": "Summary",
                "description": "Brief summary of the content"
            },
            {
                "type": "multiSelect",
                "key": "keywords",
                "displayName": "Keywords",
                "description": "Key topics and terms from the content",
                "options": [
                    {"key": "keyword"}  # Will be dynamically populated
                ]
            },
            {
                "type": "float",
                "key": "duration",
                "displayName": "Duration",
                "description": "Duration of the content in seconds"
            }
        ]
    }

def format_ai_metadata(transcript_data: Dict, keywords: List[str], summary: str) -> Dict:
    """
    Format transcript, keywords, and summary into Box AI metadata format.
    
    Args:
        transcript_data (dict): Dictionary containing transcript data with:
            - text (str): Full transcript text
            - segments (list): List of segments with timestamps and text
        keywords (list): List of extracted keywords/phrases
        summary (str): Generated summary of the transcript
        
    Returns:
        dict: Box AI metadata format for extraction
    """
    try:
        # Calculate total duration from transcript segments
        duration = max(segment["end"] for segment in transcript_data["segments"])
        
        # Format the metadata
        metadata = {
            "items": [
                {
                    "type": "file",
                    "content": {
                        "transcript": transcript_data["text"],
                        "summary": summary,
                        "keywords": keywords,
                        "duration": duration
                    }
                }
            ],
            "metadata_template": create_metadata_template()
        }
        
        return metadata
        
    except Exception as e:
        raise ValueError(f"Error formatting AI metadata: {str(e)}")

def test_formatter():
    """Test function for AI metadata formatting"""
    # Sample transcript data
    transcript_data = {
        "text": "Hello, my name is William Higgins...",
        "segments": [
            {
                "text": "Hello, my name is William Higgins.",
                "start": 0.0,
                "end": 3.5
            },
            {
                "text": "I am a manager in the Solutions Engineering Department.",
                "start": 3.5,
                "end": 7.0
            }
        ]
    }

    # Sample keywords
    keywords = [
        "William Higgins",
        "Solutions Engineering Department",
        "Box.com"
    ]

    # Sample summary
    summary = "William Higgins introduces himself as a manager in the Solutions Engineering Department at Box.com."

    try:
        # Format metadata
        metadata = format_ai_metadata(transcript_data, keywords, summary)
        
        # Print formatted metadata
        print("\nFormatted Box AI Metadata:")
        print(json.dumps(metadata, indent=2))
        
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")

if __name__ == "__main__":
    test_formatter() 