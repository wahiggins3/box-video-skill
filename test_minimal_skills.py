#!/usr/bin/env python3

import json
import time
import requests

def create_minimal_skills_card():
    """Create the absolute minimum valid Skills card."""
    invocation_id = f"box-video-skill-{int(time.time())}"
    
    return {
        "cards": [
            {
                "type": "skill_card",
                "skill_card_type": "text",
                "skill_card_title": {
                    "code": "test",
                    "message": "Test"
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
                        "text": "Hello world test."
                    }
                ]
            }
        ]
    }

def test_upload_minimal_card(file_id, write_token):
    """Test uploading a minimal card to Box."""
    
    # Get the write token
    if isinstance(write_token, dict) and 'write' in write_token:
        token = write_token['write']['access_token']
    else:
        token = write_token
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Create minimal metadata
    metadata = create_minimal_skills_card()
    
    print("Testing minimal Skills card upload...")
    print(f"File ID: {file_id}")
    print(f"Metadata: {json.dumps(metadata, indent=2)}")
    
    # Upload to Box
    url = f'https://api.box.com/2.0/files/{file_id}/metadata/global/boxSkillsCards'
    
    try:
        response = requests.post(url, headers=headers, json=metadata)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Minimal Skills card uploaded!")
            return True
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Minimal Skills Card Test")
    print("=" * 30)
    
    # This would need to be called with actual file_id and write_token
    # from a webhook payload for real testing
    metadata = create_minimal_skills_card()
    print("Generated minimal metadata:")
    print(json.dumps(metadata, indent=2)) 