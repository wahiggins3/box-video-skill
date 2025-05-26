#!/usr/bin/env python3

import json
import time
from skills_formatter import format_metadata, create_error_card

def create_minimal_transcript_card():
    """Create a minimal transcript card to test the format."""
    invocation_id = f"box-video-skill-{int(time.time())}"
    
    # Minimal transcript card - just like the working error card structure
    return {
        "cards": [
            {
                "type": "skill_card",
                "skill_card_type": "transcript",
                "skill_card_title": {
                    "code": "transcript",
                    "message": "Transcript"
                },
                "skill": {
                    "type": "service",
                    "id": "box-video-skill"
                },
                "invocation": {
                    "type": "skill_invocation",
                    "id": invocation_id
                },
                "entries": [
                    {
                        "text": "Hello world test transcript.",
                        "appears": [
                            {
                                "start": 1
                            }
                        ]
                    }
                ]
            }
        ]
    }

def create_minimal_summary_card():
    """Create a minimal summary card to test the format."""
    invocation_id = f"box-video-skill-{int(time.time())}"
    
    return {
        "cards": [
            {
                "type": "skill_card",
                "skill_card_type": "text",
                "skill_card_title": {
                    "code": "summary",
                    "message": "Summary"
                },
                "skill": {
                    "type": "service",
                    "id": "box-video-skill"
                },
                "invocation": {
                    "type": "skill_invocation",
                    "id": invocation_id
                },
                "entries": [
                    {
                        "type": "text",
                        "text": "This is a test summary."
                    }
                ]
            }
        ]
    }

def create_minimal_keywords_card():
    """Create a minimal keywords card to test the format."""
    invocation_id = f"box-video-skill-{int(time.time())}"
    
    return {
        "cards": [
            {
                "type": "skill_card",
                "skill_card_type": "keyword",
                "skill_card_title": {
                    "code": "keywords",
                    "message": "Keywords"
                },
                "skill": {
                    "type": "service",
                    "id": "box-video-skill"
                },
                "invocation": {
                    "type": "skill_invocation",
                    "id": invocation_id
                },
                "entries": [
                    {
                        "type": "text",
                        "text": "test"
                    },
                    {
                        "type": "text", 
                        "text": "keywords"
                    }
                ]
            }
        ]
    }

def test_real_data_format():
    """Test the format_metadata function with real-like data."""
    
    # Simulate real transcript data
    transcript_data = {
        "text": "Hello world. This is a test.",
        "segments": [
            {"start": 0.0, "end": 2.5, "text": "Hello world."},
            {"start": 2.5, "end": 5.0, "text": "This is a test."}
        ]
    }
    
    keywords = ["hello", "world", "test"]
    summary = "A simple test transcript."
    
    try:
        metadata = format_metadata(transcript_data, keywords, summary)
        print("✅ Real data format_metadata succeeded")
        print(f"📊 Generated {len(metadata.get('cards', []))} cards")
        return metadata
    except Exception as e:
        print(f"❌ Real data format_metadata failed: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Testing Box Skills Card Formats")
    print("=" * 50)
    
    # Test minimal formats
    print("\n1️⃣  Testing minimal transcript card:")
    transcript_card = create_minimal_transcript_card()
    print(json.dumps(transcript_card, indent=2))
    
    print("\n2️⃣  Testing minimal summary card:")
    summary_card = create_minimal_summary_card()
    print(json.dumps(summary_card, indent=2))
    
    print("\n3️⃣  Testing minimal keywords card:")
    keywords_card = create_minimal_keywords_card()
    print(json.dumps(keywords_card, indent=2))
    
    print("\n4️⃣  Testing real data format:")
    real_metadata = test_real_data_format()
    if real_metadata:
        print("✅ Real metadata structure:")
        # Only print the structure, not the full data
        for i, card in enumerate(real_metadata.get('cards', [])):
            print(f"   Card {i+1}: {card.get('skill_card_type')} with {len(card.get('entries', []))} entries")
    
    print("\n🔍 Key differences to investigate:")
    print("   - Timestamp format (integers vs floats)")
    print("   - Required vs optional fields")
    print("   - Field order")
    print("   - Data validation rules") 