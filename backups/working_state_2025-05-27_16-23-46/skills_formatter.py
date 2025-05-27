# Placeholder for formatting Box Skills metadata
import json
import time

def create_error_card(error_message):
    """
    Create a simple error card that can be displayed in Box.
    
    Args:
        error_message (str): The error message to display
        
    Returns:
        dict: A valid Box Skills card showing the error
    """
    invocation_id = f"box-video-skill-{int(time.time())}"
    
    error_metadata = {
        "cards": [
            {
                "type": "skill_card",
                "skill_card_type": "status",
                "status": {
                    "code": "error",
                    "message": "An error occurred while processing this file"
                },
                "skill_card_title": {
                    "code": "processing-error",
                    "message": "Processing Error"
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
                        "text": f"⚠️ Error processing this file:\n\n{error_message}\n\nPlease contact your administrator for assistance."
                    }
                ]
            }
        ]
    }
    
    # Validate the error card (it should always be valid)
    is_valid, validation_msg = validate_metadata(error_metadata)
    if not is_valid:
        # If somehow our error card is invalid, create an even simpler one
        return {
            "cards": [
                {
                    "type": "skill_card",
                    "skill_card_type": "status",
                    "status": {
                        "code": "error",
                        "message": "System Error"
                    },
                    "skill_card_title": {
                        "code": "system-error",
                        "message": "System Error"
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
                            "text": "Critical error occurred while processing this file."
                        }
                    ]
                }
            ]
        }
    
    return error_metadata

def validate_metadata(metadata):
    """
    Validate that the metadata follows Box Skills format requirements.
    SIMPLIFIED for transcript-only debugging.
    
    Args:
        metadata (dict): The metadata to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        print("🔍 Validating metadata structure...")
        
        # Check top-level structure
        if not isinstance(metadata, dict):
            return False, "Metadata must be a dictionary"
            
        if "cards" not in metadata:
            return False, "Metadata must have a 'cards' key"
            
        if not isinstance(metadata["cards"], list):
            return False, "The 'cards' value must be a list"
            
        print(f"✅ Top-level structure valid. Found {len(metadata['cards'])} cards")
            
        # Check each card - SIMPLIFIED for transcript only
        for i, card in enumerate(metadata["cards"]):
            print(f"🔍 Validating card {i+1}...")
            
            # Check required card fields
            if "type" not in card or card["type"] != "skill_card":
                return False, f"Card {i+1} must have type: 'skill_card'"
                
            if "skill_card_type" not in card:
                return False, f"Card {i+1} missing 'skill_card_type'"
                
            # Allow transcript, text, and status cards (for summary and errors)
            allowed_types = ["transcript", "text", "status"]
            if card["skill_card_type"] not in allowed_types:
                print(f"⚠️  Unsupported card type: {card['skill_card_type']}")
                print(f"⚠️  Allowed types: {allowed_types}")
                # Allow it but warn
                
            if "skill_card_title" not in card:
                return False, f"Card {i+1} missing 'skill_card_title'"
                
            # Check skill and invocation on each card
            if "skill" not in card:
                return False, f"Card {i+1} must have a 'skill' object"
                
            if "invocation" not in card:
                return False, f"Card {i+1} must have an 'invocation' object"
                
            if "entries" not in card:
                return False, f"Card {i+1} missing 'entries'"
                
            if not isinstance(card["entries"], list):
                return False, f"Card {i+1} 'entries' must be a list"
                
            print(f"✅ Card {i+1} basic structure valid. Checking {len(card['entries'])} entries...")
                
            # Check entries - SIMPLIFIED for transcript
            for j, entry in enumerate(card["entries"]):
                if "text" not in entry:
                    return False, f"Entry {j+1} in card {i+1} missing 'text' field"
                    
                # Only check transcript-specific fields for transcript cards
                if card["skill_card_type"] == "transcript":
                    if "appears" not in entry:
                        return False, f"Transcript entry {j+1} missing 'appears' field"
                    if not isinstance(entry["appears"], list):
                        return False, f"Transcript entry {j+1} 'appears' must be a list"
                    for timestamp in entry["appears"]:
                        if "start" not in timestamp:
                            return False, f"Transcript entry {j+1} has invalid timestamp format - missing 'start'"
                        if not isinstance(timestamp["start"], int):
                            return False, f"Transcript entry {j+1} 'start' timestamp must be an integer (seconds)"
            
            print(f"✅ Card {i+1} entries valid")
        
        print("✅ All validation checks passed!")
        return True, ""
        
    except Exception as e:
        print(f"❌ Validation exception: {str(e)}")
        return False, f"Validation error: {str(e)}"

def format_metadata(transcript_data, keywords=None, summary=None):
    """
    Format transcript data into Box Skills metadata format.
    Supports TRANSCRIPT and SUMMARY cards.
    
    Args:
        transcript_data (dict): Dictionary containing transcript data with:
            - text (str): Full transcript text
            - segments (list): List of segments with timestamps and text
        keywords (list): COMMENTED OUT - List of extracted keywords/phrases
        summary (str): Generated summary of the transcript (optional)
        
    Returns:
        dict: Box Skills metadata format with transcript card and optional summary card
        
    Raises:
        ValueError: If the generated metadata is invalid and error card creation also fails
    """
    try:
        print(f"📝 Creating transcript card with {len(transcript_data.get('segments', []))} segments")
        
        # Create transcript entries - USE ALL SEGMENTS as requested
        transcript_entries = []
        max_timestamp = 0
        
        for i, segment in enumerate(transcript_data["segments"]):
            # Sanitize text but don't truncate too aggressively
            text = segment["text"].strip()
            # Remove any problematic characters
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
            
            start_time = int(segment["start"])
            max_timestamp = max(max_timestamp, start_time)
            
            entry = {
                "text": text,
                "appears": [{
                    "start": start_time  # Box API uses seconds as integers
                }]
            }
            
            transcript_entries.append(entry)
            print(f"  Entry {i+1}: '{text[:50]}...' at {start_time}s")

        print(f"📊 Total entries created: {len(transcript_entries)}")
        print(f"📊 Duration: {max_timestamp} seconds ({max_timestamp // 60}:{max_timestamp % 60:02d})")

        # Generate a unique invocation ID
        invocation_id = f"box-video-skill-{int(time.time())}"
        print(f"🔧 Using invocation ID: {invocation_id}")

        # Build MINIMAL metadata in Box Skills format - TRANSCRIPT CARD ONLY
        metadata = {
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
                    "duration": max_timestamp,  # Add total duration in seconds
                    "entries": transcript_entries
                }
            ]
        }
        
        # TEMPORARILY COMMENTED OUT - Add summary card if summary is provided
        # Will upload summary separately to avoid Box API 500 errors
        """
        if summary and summary.strip():
            print(f"📝 Adding summary card: {len(summary)} characters")
            summary_card = {
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
                        "text": summary.strip()
                    }
                ]
            }
            metadata["cards"].append(summary_card)
        """
        
        # COMMENTED OUT - Keywords card
        # Will bring this back once summary card is working
        """
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
                    "entries": keyword_entries
                }
        """
        
        print(f"✅ Created metadata with {len(metadata['cards'])} card(s)")
        print(f"   Card 1: {metadata['cards'][0]['skill_card_type']} with {len(metadata['cards'][0]['entries'])} entries")
        
        # Log additional cards if present
        for i in range(1, len(metadata['cards'])):
            card = metadata['cards'][i]
            print(f"   Card {i+1}: {card['skill_card_type']} with {len(card['entries'])} entries")
        
        # Validate the metadata before returning
        is_valid, error_msg = validate_metadata(metadata)
        if not is_valid:
            print(f"❌ Validation failed: {error_msg}")
            error_details = f"Metadata validation failed: {error_msg}"
            return create_error_card(error_details)

        print("✅ Metadata validation passed")
        return metadata
        
    except Exception as e:
        print(f"❌ Exception in format_metadata: {str(e)}")
        return create_error_card(f"Error formatting metadata: {str(e)}")


def create_summary_card(summary, invocation_id=None):
    """
    Create a standalone summary card that can be uploaded separately.
    
    Args:
        summary (str): The summary text
        invocation_id (str): Optional invocation ID, will generate one if not provided
        
    Returns:
        dict: Box Skills metadata format with single summary card
    """
    if not invocation_id:
        invocation_id = f"box-video-skill-{int(time.time())}"
    
    return {
        "cards": [
            {
                "type": "skill_card",
                "skill_card_type": "status",
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
                "status": {
                    "code": "success",
                    "message": summary.strip()
                }
            }
        ]
    }

def create_processing_info_card(transcript_info=None, summary_info=None, file_duration=None, invocation_id=None):
    """
    Create a processing information card that shows details about the AI services used.
    
    Args:
        transcript_info (dict): Processing info from transcription
        summary_info (dict): Processing info from summary generation
        file_duration (float): Duration of the audio file in seconds
        invocation_id (str): Optional invocation ID, will generate one if not provided
        
    Returns:
        dict: Box Skills metadata format with processing info status card
    """
    if not invocation_id:
        invocation_id = f"box-video-skill-{int(time.time())}"
    
    # Build processing details message with simple text formatting
    details = []
    
    if transcript_info:
        file_size_mb = round(transcript_info.get('file_size', 0) / 1024 / 1024, 2)
        details.append("🎤 TRANSCRIPTION")
        details.append(f"  Service: {transcript_info.get('service', 'Unknown')}")
        details.append(f"  Model: {transcript_info.get('model', 'Unknown')}")
        details.append(f"  Processing time: {transcript_info.get('processing_time', 0)}s")
        details.append(f"  File size: {file_size_mb}MB")
        details.append("")  # Empty line for spacing
        
    if summary_info:
        input_length_k = round(summary_info.get('input_length', 0) / 1000, 1)
        details.append("📝 SUMMARY GENERATION")
        details.append(f"  Service: {summary_info.get('service', 'Unknown')}")
        details.append(f"  Model: {summary_info.get('model', 'Unknown')}")
        details.append(f"  Processing time: {summary_info.get('processing_time', 0)}s")
        details.append(f"  Input text: {input_length_k}k characters")
        details.append("")
        
    if keywords_info:
        input_length_k = round(keywords_info.get('input_length', 0) / 1000, 1)
        details.append("🏷️ KEYWORD EXTRACTION")
        details.append(f"  Service: {keywords_info.get('service', 'Unknown')}")
        details.append(f"  Model: {keywords_info.get('model', 'Unknown')}")
        details.append(f"  Processing time: {keywords_info.get('processing_time', 0)}s")
        details.append(f"  Input text: {input_length_k}k characters")
        details.append("")
    
    # File and performance summary
    details.append("📊 PERFORMANCE SUMMARY")
    
    if file_duration:
        duration_min = int(file_duration // 60)
        duration_sec = int(file_duration % 60)
        details.append(f"  Audio duration: {duration_min}:{duration_sec:02d}")
    
    total_time = 0
    if transcript_info:
        total_time += transcript_info.get('processing_time', 0)
    if summary_info:
        total_time += summary_info.get('processing_time', 0)
    if keywords_info:
        total_time += keywords_info.get('processing_time', 0)
    
    if total_time > 0:
        details.append(f"  Total AI processing: {round(total_time, 2)}s")
        
        if file_duration and total_time < file_duration:
            efficiency = round((file_duration / total_time), 1)
            details.append(f"  Efficiency: {efficiency}x faster than real-time ⚡")
    
    details.append("")
    details.append("✅ Processing completed successfully!")
    
    message = "\n".join(details) if details else "Processing completed successfully"
    
    return {
        "cards": [
            {
                "type": "skill_card",
                "skill_card_type": "status",
                "skill_card_title": {
                    "code": "processing_info",
                    "message": "🤖 AI Processing Details"
                },
                "skill": {
                    "type": "service",
                    "id": "box-video-skill"
                },
                "invocation": {
                    "type": "skill_invocation",
                    "id": invocation_id
                },
                "status": {
                    "code": "success",
                    "message": message
                }
            }
        ]
    }

def create_all_cards(transcript_data, summary, keywords, transcript_info, summary_info, keywords_info, file_duration, invocation_id=None):
    """
    Create all Box Skills cards in the desired order: Summary, Keywords, Transcript, AI Details.
    
    Args:
        transcript_data (dict): Transcript data with segments
        summary (str): AI-generated summary
        keywords (list): List of extracted keywords
        transcript_info (dict): Processing info from transcription
        summary_info (dict): Processing info from summary generation
        keywords_info (dict): Processing info from keyword extraction
        file_duration (float): Duration of the audio file in seconds
        invocation_id (str): Optional invocation ID, will generate one if not provided
        
    Returns:
        dict: Box Skills metadata format with all cards in desired order
    """
    if not invocation_id:
        invocation_id = f"box-video-skill-{int(time.time())}"
    
    all_cards = []
    
    # 1. Summary card (appears first)
    if summary and summary.strip():
        summary_card = {
            "type": "skill_card",
            "skill_card_type": "status",
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
            "status": {
                "code": "success",
                "message": summary.strip()
            }
        }
        all_cards.append(summary_card)
    
    # 2. Keywords card (appears second)
    if keywords and len(keywords) > 0:
        keyword_entries = []
        for keyword in keywords:
            if keyword.strip():  # Only add non-empty keywords
                keyword_entries.append({
                    "text": keyword.strip()
                })
        
        if keyword_entries:  # Only add card if we have valid keywords
            keywords_card = {
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
                "entries": keyword_entries
            }
            all_cards.append(keywords_card)
    
    # 3. Transcript card (appears third)
    transcript_entries = []
    max_timestamp = 0
    
    for i, segment in enumerate(transcript_data["segments"]):
        # Sanitize text but don't truncate too aggressively
        text = segment["text"].strip()
        # Remove any problematic characters
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        start_time = int(segment["start"])
        max_timestamp = max(max_timestamp, start_time)
        
        entry = {
            "text": text,
            "appears": [{
                "start": start_time  # Box API uses seconds as integers
            }]
        }
        
        transcript_entries.append(entry)
    
    transcript_card = {
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
        "duration": max_timestamp,  # Add total duration in seconds
        "entries": transcript_entries
    }
    all_cards.append(transcript_card)
    
    # 4. AI Processing details card (appears last)
    details = []
    
    if transcript_info:
        file_size_mb = round(transcript_info.get('file_size', 0) / 1024 / 1024, 2)
        details.append("🎤 TRANSCRIPTION")
        details.append(f"  Service: {transcript_info.get('service', 'Unknown')}")
        details.append(f"  Model: {transcript_info.get('model', 'Unknown')}")
        details.append(f"  Processing time: {transcript_info.get('processing_time', 0)}s")
        details.append(f"  File size: {file_size_mb}MB")
        details.append("")
        
    if summary_info:
        input_length_k = round(summary_info.get('input_length', 0) / 1000, 1)
        details.append("📝 SUMMARY GENERATION")
        details.append(f"  Service: {summary_info.get('service', 'Unknown')}")
        details.append(f"  Model: {summary_info.get('model', 'Unknown')}")
        details.append(f"  Processing time: {summary_info.get('processing_time', 0)}s")
        details.append(f"  Input text: {input_length_k}k characters")
        details.append("")
        
    if keywords_info:
        input_length_k = round(keywords_info.get('input_length', 0) / 1000, 1)
        details.append("🏷️ KEYWORD EXTRACTION")
        details.append(f"  Service: {keywords_info.get('service', 'Unknown')}")
        details.append(f"  Model: {keywords_info.get('model', 'Unknown')}")
        details.append(f"  Processing time: {keywords_info.get('processing_time', 0)}s")
        details.append(f"  Input text: {input_length_k}k characters")
        details.append("")
    
    details.append("📊 PERFORMANCE SUMMARY")
    
    if file_duration:
        duration_min = int(file_duration // 60)
        duration_sec = int(file_duration % 60)
        details.append(f"  Audio duration: {duration_min}:{duration_sec:02d}")
    
    total_time = 0
    if transcript_info:
        total_time += transcript_info.get('processing_time', 0)
    if summary_info:
        total_time += summary_info.get('processing_time', 0)
    if keywords_info:
        total_time += keywords_info.get('processing_time', 0)
    
    if total_time > 0:
        details.append(f"  Total AI processing: {round(total_time, 2)}s")
        
        if file_duration and total_time < file_duration:
            efficiency = round((file_duration / total_time), 1)
            details.append(f"  Efficiency: {efficiency}x faster than real-time ⚡")
    
    details.append("")
    details.append("✅ Processing completed successfully!")
    
    ai_details_card = {
        "type": "skill_card",
        "skill_card_type": "status",
        "skill_card_title": {
            "code": "processing_info",
            "message": "🤖 AI Processing Details"
        },
        "skill": {
            "type": "service",
            "id": "box-video-skill"
        },
        "invocation": {
            "type": "skill_invocation",
            "id": invocation_id
        },
        "status": {
            "code": "success",
            "message": "\n".join(details)
        }
    }
    all_cards.append(ai_details_card)
    
    return {"cards": all_cards}

def test_formatter():
    """Test function for metadata formatting"""
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
    summary = "William Higgins introduces himself as a manager in the Solutions Engineering Department at Box.com. He is currently watching the movie Bullet Train while listening to an Atlanta Braves baseball game."

    try:
        # Format metadata
        metadata = format_metadata(transcript_data, keywords, summary)
        
        # Print formatted metadata
        print("\nFormatted Box Skills Metadata:")
        print(json.dumps(metadata, indent=2))
        
        # Check if this is an error card
        if len(metadata["cards"]) == 1 and metadata["cards"][0]["skill_card_title"]["message"] == "Processing Error":
            print("\n⚠️ Generated error card due to validation failure")
        else:
            print("\nMetadata validation: Passed ✓")
        
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")


if __name__ == "__main__":
    test_formatter()

    # Test error card generation
    print("\nTesting error card generation:")
    error_card = create_error_card("Test error message")
    print(json.dumps(error_card, indent=2))
