from flask import Flask, request, jsonify
import logging
import subprocess
from box_client import download_file_from_box
from whisper_client import transcribe_audio
from gpt_keywords import extract_keywords, generate_summary
from skills_formatter import format_metadata, create_error_card
import os
import json
import requests

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def upload_metadata_to_box(file_id, metadata, write_token):
    """
    Upload metadata back to Box using the Skills Write API.
    First checks if Skills cards exist, then creates or updates accordingly.
    
    Args:
        file_id (str): The Box file ID
        metadata (dict): The metadata to upload
        write_token (str): The write token from the webhook
    """
    try:
        logger.info("🚀 STARTING BOX SKILLS API UPLOAD")
        logger.info("=" * 80)
        
        # Extract and validate the write token
        if isinstance(write_token, dict):
            if 'write' in write_token and 'access_token' in write_token['write']:
                token = write_token['write']['access_token']
                logger.info("✅ Using write token from dictionary")
            elif 'read' in write_token and 'access_token' in write_token['read']:
                token = write_token['read']['access_token']
                logger.info("⚠️  Using read token as fallback")
            else:
                logger.error(f"❌ Invalid token structure: {write_token}")
                raise ValueError("Invalid token structure provided")
        else:
            token = str(write_token)
            logger.info("✅ Using token as string")
        
        logger.info(f"🔑 Token prefix: {token[:20]}..." if token else "No token")
        logger.info(f"📁 File ID: {file_id}")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        logger.info(f"📋 Request headers prepared: {list(headers.keys())}")
        
        base_url = f'https://api.box.com/2.0/files/{file_id}/metadata/global/boxSkillsCards'
        logger.info(f"🌐 Using Box Skills API endpoint: {base_url}")
        
        # First, check if Skills cards already exist on the file
        logger.info("🔍 STEP 1: Checking if Skills cards already exist")
        logger.info("-" * 40)
        
        check_response = requests.get(
            base_url,
            headers=headers
        )
        
        logger.info(f"📊 GET Response Status: {check_response.status_code}")
        logger.info(f"📊 GET Response Headers: {dict(check_response.headers)}")
        logger.info(f"📊 GET Response Body: {check_response.text}")
        
        if check_response.status_code == 200:
            # Skills cards exist, use PUT to update with JSON Patch format
            logger.info("📝 STEP 2: Skills cards exist, updating with PUT (JSON Patch)")
            logger.info("-" * 40)
            
            # Get the existing cards to understand the current structure
            existing_data = check_response.json()
            existing_cards = existing_data.get('cards', [])
            existing_count = len(existing_cards)
            new_cards = metadata.get('cards', [])
            new_count = len(new_cards)
            
            logger.info(f"📊 Existing cards: {existing_count}, New cards: {new_count}")
            
            # For updating, we need to use JSON Patch format
            # Content-Type should be application/json-patch+json
            patch_headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json-patch+json'
            }
            
            # Build JSON Patch operations to handle card count differences
            patch_operations = []
            for i, card in enumerate(new_cards):
                if i < existing_count:
                    # Replace existing card
                    patch_operations.append({
                        "op": "replace",
                        "path": f"/cards/{i}",
                        "value": card
                    })
                else:
                    # Add new card
                    patch_operations.append({
                        "op": "add", 
                        "path": f"/cards/-",
                        "value": card
                    })
            
            # If we have fewer new cards than existing cards, remove extra ones
            for i in range(new_count, existing_count):
                patch_operations.append({
                    "op": "remove",
                    "path": f"/cards/{new_count}"  # Always remove at new_count position
                })
            
            logger.info(f"📋 JSON Patch operations: {json.dumps(patch_operations, indent=2)}")
            
            response = requests.put(
                base_url,
                headers=patch_headers,
                json=patch_operations
            )
            
            logger.info(f"📊 PUT Response Status: {response.status_code}")
            logger.info(f"📊 PUT Response Headers: {dict(response.headers)}")
            logger.info(f"📊 PUT Response Body: {response.text}")
            
        elif check_response.status_code == 404:
            # No Skills cards exist, use POST to create
            logger.info("📝 STEP 2: No Skills cards exist, creating with POST")
            logger.info("-" * 40)
            
            logger.info(f"📋 POST Payload: {json.dumps(metadata, indent=2)}")
            
            response = requests.post(
                base_url,
                headers=headers,
                json=metadata
            )
            
            logger.info(f"📊 POST Response Status: {response.status_code}")
            logger.info(f"📊 POST Response Headers: {dict(response.headers)}")
            logger.info(f"📊 POST Response Body: {response.text}")
            
        else:
            # Unexpected response from check
            logger.error(f"❌ Unexpected response from Skills cards check: {check_response.status_code}")
            logger.error(f"❌ Response body: {check_response.text}")
            raise ValueError(f"Unexpected response: {check_response.status_code}")
        
        logger.info("=" * 80)
        
        # Check if the upload was successful
        if response.status_code in [200, 201]:
            logger.info(f"✅ SUCCESS: Metadata uploaded successfully (Status: {response.status_code})")
            return True
        else:
            error_msg = f"Failed to upload metadata: {response.text}"
            logger.error(f"❌ FAILED: {error_msg}")
            
            # Try to upload an error card as fallback
            try:
                logger.info("🔄 Attempting to upload error card as fallback...")
                error_card = create_error_card(f"Upload failed: {response.status_code}")
                error_response = requests.post(
                    base_url,
                    headers=headers,
                    json=error_card
                )
                logger.info(f"📊 Error card response: {error_response.status_code}")
                
                if error_response.status_code not in [200, 201]:
                    logger.error(f"Failed to upload error card: {error_response.text}")
                    
            except Exception as fallback_error:
                logger.error(f"Failed to upload error card: {fallback_error}")
            
            return False
            
    except Exception as e:
        logger.error(f"❌ EXCEPTION in upload_metadata_to_box: {str(e)}")
        logger.error(f"❌ Exception type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

def convert_video_to_audio(video_path):
    """Convert video to audio using ffmpeg."""
    audio_path = video_path + '.mp3'
    try:
        # First, check if the input file exists
        if not os.path.exists(video_path):
            raise Exception(f"Input file not found: {video_path}")
            
        # Use ffprobe to check if the file has an audio stream
        probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        
        if not result.stdout.strip():
            raise Exception("No audio stream found in the input file")
        
        # Convert to MP3 format (supported by Whisper API)
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'libmp3lame',
            '-ac', '2',  # Stereo
            '-ar', '44100',  # 44.1kHz sample rate
            '-ab', '192k',  # 192kbps bitrate
            '-y',  # Overwrite output file
            audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"ffmpeg conversion failed: {result.stderr}")
            
        # Verify the output file exists and has size > 0
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            raise Exception("Failed to create valid audio file")
            
        logger.info(f"Successfully converted video to audio: {audio_path}")
        return audio_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to convert video to audio: {str(e)}")
        logger.error(f"ffmpeg stderr: {e.stderr}")
        raise Exception(f"Failed to convert video to audio: {str(e)}")
    except Exception as e:
        logger.error(f"Error during video conversion: {str(e)}")
        raise

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        logger.info("Received webhook request")
        data = request.json
        logger.info(f"Webhook payload: {json.dumps(data)}")
        
        # Extract file ID and token from the request
        file_id = data.get("source", {}).get("id")
        token = data.get("token")
        file_name = data.get("source", {}).get("name", "").lower()
        
        logger.info(f"File ID: {file_id}")
        logger.info(f"File name: {file_name}")
        logger.info(f"Token present: {bool(token)}")
        logger.info(f"Token type: {type(token)}")
        logger.info(f"Token structure: {json.dumps(token) if isinstance(token, dict) else 'not a dict'}")
        
        if not file_id:
            logger.error("Missing file ID")
            return jsonify({"error": "Missing file ID"}), 400
        if not token:
            logger.error("Missing token")
            return jsonify({"error": "Missing token"}), 400
        if not isinstance(token, dict) or not token.get('read', {}).get('access_token'):
            logger.error("Invalid token format")
            return jsonify({"error": "Invalid token format"}), 400

        # Download and process the video
        try:
            video_path = download_file_from_box(file_id, token)
            logger.info(f"Successfully downloaded file to {video_path}")
        except Exception as e:
            error_msg = f"Failed to download file: {str(e)}"
            logger.error(error_msg)
            # Create and upload error card
            error_metadata = create_error_card(error_msg)
            try:
                upload_metadata_to_box(file_id, error_metadata, token)
                logger.info("Successfully uploaded error card to Box")
            except Exception as upload_err:
                logger.error(f"Failed to upload error card: {str(upload_err)}")
            return jsonify({"error": error_msg}), 500
        
        try:
            # Convert to audio if needed
            audio_path = video_path
            supported_audio = ('.mp3', '.m4a', '.wav', '.flac', '.ogg', '.webm')
            if not file_name.endswith(supported_audio):
                audio_path = convert_video_to_audio(video_path)
                logger.info(f"Successfully converted to audio: {audio_path}")
            
            # Get transcript with timestamps
            transcript_data = transcribe_audio(audio_path)
            logger.info("Successfully transcribed audio")
            logger.info(f"Transcript data structure: {json.dumps(transcript_data)}")
            
            # Process with Whisper
            logger.info("Starting Whisper transcription")
            transcript_data = transcribe_audio(audio_path)
            logger.info(f"Whisper transcription completed. Segments: {len(transcript_data.get('segments', []))}")
            
            # COMMENTED OUT - Keywords and Summary processing
            # Will bring these back once transcript card is working
            """
            # Extract keywords using GPT-4
            logger.info("Starting keyword extraction with GPT-4")
            keywords = extract_keywords(transcript_data["text"])
            logger.info(f"Keyword extraction completed. Keywords: {len(keywords)}")
            
            # Generate summary using GPT-4
            logger.info("Starting summary generation with GPT-4")
            summary = generate_summary(transcript_data["text"])
            logger.info(f"Summary generation completed. Length: {len(summary) if summary else 0} characters")
            """
            
            # For now, pass None for keywords and summary
            keywords = None
            summary = None
            logger.info("⚠️  SKIPPING keywords and summary processing for debugging")
            
            # Format metadata for Box Skills
            logger.info("Formatting metadata for Box Skills")
            metadata = format_metadata(transcript_data, keywords, summary)
            
            # EXTENSIVE LOGGING - Show exactly what we're about to send
            logger.info("=" * 60)
            logger.info("📤 METADATA PAYLOAD DETAILS")
            logger.info("=" * 60)
            logger.info(f"📊 Metadata type: {type(metadata)}")
            logger.info(f"📊 Metadata keys: {metadata.keys() if isinstance(metadata, dict) else 'Not a dict'}")
            if isinstance(metadata, dict) and 'cards' in metadata:
                logger.info(f"📊 Number of cards: {len(metadata['cards'])}")
                for i, card in enumerate(metadata['cards']):
                    logger.info(f"📊 Card {i+1}: type={card.get('skill_card_type')}, entries={len(card.get('entries', []))}")
            
            # Log the full JSON payload
            metadata_json = json.dumps(metadata, indent=2)
            logger.info(f"📋 FULL JSON PAYLOAD:\n{metadata_json}")
            logger.info("=" * 60)
            
            # Check if we got an error card
            is_error_card = (
                isinstance(metadata, dict) and
                "cards" in metadata and
                len(metadata["cards"]) == 1 and 
                metadata["cards"][0].get("type") == "skill_card" and
                metadata["cards"][0].get("skill_card_type") == "text" and
                metadata["cards"][0].get("skill_card_title", {}).get("message") == "Processing Error"
            )
            
            if is_error_card:
                logger.warning("Generated error card due to metadata formatting issues")
            else:
                logger.info("Successfully formatted metadata")
            
            # Upload metadata back to Box
            upload_metadata_to_box(file_id, metadata, token)
            logger.info("Successfully uploaded metadata to Box")
            
        except Exception as e:
            error_msg = f"Failed during processing: {str(e)}"
            logger.error(error_msg)
            # Create and upload error card
            error_metadata = create_error_card(error_msg)
            try:
                upload_metadata_to_box(file_id, error_metadata, token)
                logger.info("Successfully uploaded error card to Box")
            except Exception as upload_err:
                logger.error(f"Failed to upload error card: {str(upload_err)}")
            return jsonify({"error": error_msg}), 500
        finally:
            # Clean up temporary files
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path) and audio_path != video_path:
                os.remove(audio_path)
            
        return jsonify({"message": "Processing completed successfully"})
            
    except Exception as e:
        error_msg = f"Webhook error: {str(e)}"
        logger.error(error_msg)
        # Create and upload error card for unexpected errors
        try:
            error_metadata = create_error_card(error_msg)
            upload_metadata_to_box(file_id, error_metadata, token)
            logger.info("Successfully uploaded error card to Box")
        except Exception as upload_err:
            logger.error(f"Failed to upload error card: {str(upload_err)}")
        return jsonify({"error": error_msg}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
