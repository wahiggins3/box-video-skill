import os
from boxsdk import Client, OAuth2
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def authenticate_box():
    """Authenticate with Box using OAuth2"""
    auth = OAuth2(
        client_id=os.getenv('BOX_CLIENT_ID'),
        client_secret=os.getenv('BOX_CLIENT_SECRET'),
        access_token=os.getenv('BOX_ACCESS_TOKEN')
    )
    return Client(auth)

def test_skill_with_file(file_path):
    """
    Upload a file to Box and monitor the skill processing.
    
    Args:
        file_path (str): Path to the local file to test
    """
    try:
        # Initialize Box client
        client = authenticate_box()
        
        # Get user info to confirm authentication
        user = client.user().get()
        print(f"\nAuthenticated as: {user.name}")
        
        # Create a test folder
        test_folder = client.folder('0').create_subfolder('Video Skill Test')
        print(f"\nCreated test folder: {test_folder.name}")
        
        # Upload test file
        print(f"\nUploading {file_path}...")
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            uploaded_file = test_folder.upload_stream(f, file_name)
        print(f"Uploaded file ID: {uploaded_file.id}")
        
        # Wait and check for skill cards
        print("\nWaiting for skill processing (checking every 10 seconds)...")
        max_attempts = 12  # 2 minutes total
        for i in range(max_attempts):
            time.sleep(10)
            file_info = client.file(uploaded_file.id).get()
            skill_cards = file_info.metadata('global', 'boxSkillsCards')
            
            if skill_cards:
                print("\nSkill cards found!")
                print("\nTranscript and Keywords:")
                print(skill_cards)
                break
            else:
                print(f"Attempt {i+1}/{max_attempts}: Still processing...")
        
        print("\nTest complete!")
        print(f"You can view the file here: {uploaded_file.get_url()}")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")

def main():
    # Check for Box credentials
    required_vars = ['BOX_CLIENT_ID', 'BOX_CLIENT_SECRET', 'BOX_ACCESS_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("\nError: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease add these to your .env file.")
        return
    
    # Check for test file
    test_file = "test_audio.m4a"
    if not os.path.exists(test_file):
        print(f"\nError: Test file '{test_file}' not found!")
        return
    
    # Run the test
    test_skill_with_file(test_file)

if __name__ == "__main__":
    main() 