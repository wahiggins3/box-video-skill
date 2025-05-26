import requests
import json
import os
from time import sleep

def test_webhook_locally():
    """Test the webhook endpoint running locally"""
    
    # Webhook endpoint (local Flask server)
    webhook_url = "http://localhost:5000/webhook"
    
    # Sample webhook payload (mimics Box Skills invocation)
    payload = {
        "source": {
            "id": "123456789",  # This would be the Box file ID
            "name": "test_audio.m4a"
        },
        "token": "your_box_developer_token_here",  # This would be the Box developer token
        "status": {
            "code": "pending"
        }
    }
    
    print("\n=== Testing Webhook Endpoint ===\n")
    
    try:
        # Make sure the test file exists
        if not os.path.exists("test_audio.m4a"):
            print("Error: test_audio.m4a not found!")
            return
            
        print("1. Sending webhook request...")
        print(f"Endpoint: {webhook_url}")
        print("Payload:", json.dumps(payload, indent=2))
        
        # Send POST request to webhook
        response = requests.post(webhook_url, json=payload)
        
        print("\n2. Response received!")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("\nResponse Data:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("\nError Response:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the webhook endpoint.")
        print("Make sure the Flask server is running (python main.py)")
    except Exception as e:
        print(f"\nError during testing: {str(e)}")

def main():
    # Instructions
    print("\nWebhook Testing Instructions:")
    print("1. Start the Flask server in a separate terminal:")
    print("   python main.py")
    print("\n2. Wait for the server to start (about 3 seconds)")
    print("\n3. Press Enter to begin the webhook test...")
    input()
    
    # Add a small delay to ensure server is ready
    sleep(1)
    
    # Run the webhook test
    test_webhook_locally()

if __name__ == "__main__":
    main() 