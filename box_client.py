# Box Skills file download client

import os
import tempfile
import requests
import json
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)

def parse_token(access_token):
    """
    Parse and validate the Box Skills token.
    
    Args:
        access_token (str or dict): The access token or token object from the webhook
        
    Returns:
        str: The read access token
        
    Raises:
        Exception: If no valid read token is found
    """
    try:
        # If it's a string that looks like JSON, parse it
        if isinstance(access_token, str) and access_token.strip().startswith('{'):
            try:
                token_data = json.loads(access_token)
            except json.JSONDecodeError:
                # If JSON parsing fails, treat it as a raw token
                return access_token
        elif isinstance(access_token, dict):
            token_data = access_token
        else:
            # If it's a plain string, assume it's the token
            return access_token
            
        # Extract the read token with proper scope
        if 'read' in token_data:
            read_token = token_data['read'].get('access_token')
            if read_token:
                # Log token details for debugging
                logger.info("Found read token with scopes:")
                if 'restricted_to' in token_data['read']:
                    scopes = token_data['read']['restricted_to']
                    logger.info(f"Token scopes: {scopes}")
                return read_token
                
        # If we can't find a read token in the expected structure,
        # look for any access_token field
        if 'access_token' in token_data:
            return token_data['access_token']
            
        raise Exception("No valid read token found in the access token data")
        
    except Exception as e:
        raise Exception(f"Failed to parse access token: {str(e)}")

def download_file_from_box(file_id, access_token):
    """
    Download a file from Box using its file ID and the provided access token.
    
    Args:
        file_id (str): The Box file ID to download
        access_token (str or dict): The access token or token object provided in the webhook request
        
    Returns:
        str: Path to the downloaded file
        
    Raises:
        Exception: If the download fails
    """
    try:
        # Get the read token
        read_token = parse_token(access_token)
        logger.info("Successfully parsed access token")
        
        # Set up headers with proper accept header for content
        headers = {
            'Authorization': f'Bearer {read_token}',
            'Accept': '*/*',  # Accept any content type
            'X-Box-UA': 'agent=box-skills-video'
        }
        
        # For Box Skills, we use the content endpoint
        download_url = f'https://api.box.com/2.0/files/{file_id}/content'
        
        # Create a temporary file
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f'box_file_{file_id}')
        
        # Download the file in chunks
        with requests.get(download_url, headers=headers, stream=True) as r:
            # Log response details for debugging
            logger.info(f"Download request URL: {download_url}")
            logger.info(f"Download request headers: {headers}")
            
            if r.status_code == 401 or r.status_code == 403:
                logger.error(f"Authentication error: {r.status_code}")
                logger.error(f"Response headers: {r.headers}")
                logger.error(f"Response body: {r.text}")
                
                # Try the download_url method as fallback for 403 errors  
                if r.status_code == 403:
                    logger.info("Trying download_url approach as fallback...")
                    try:
                        # First get file info to get the download URL
                        info_url = f'https://api.box.com/2.0/files/{file_id}?fields=download_url'
                        info_response = requests.get(info_url, headers=headers)
                        
                        if info_response.status_code == 200:
                            file_info = info_response.json()
                            if 'download_url' in file_info:
                                download_url = file_info['download_url']
                                logger.info(f"Got download URL: {download_url}")
                                
                                # Try downloading with the direct download URL
                                with requests.get(download_url, headers=headers, stream=True) as download_r:
                                    download_r.raise_for_status()
                                    with open(temp_file, 'wb') as f:
                                        for chunk in download_r.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                    
                                    # Check if download succeeded
                                    if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                                        logger.info(f"Successfully downloaded file using download_url method")
                                        return temp_file
                    except Exception as fallback_error:
                        logger.error(f"Download URL fallback also failed: {fallback_error}")
                
                raise Exception(f"Authentication failed with status {r.status_code}")
                
            r.raise_for_status()
            
            with open(temp_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        # Verify the file was downloaded
        if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
            raise Exception("Downloaded file is empty or does not exist")
            
        logger.info(f"Successfully downloaded file to {temp_file}")
        return temp_file
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to download file from Box: {str(e)}"
        if hasattr(e, 'response'):
            error_msg += f"\nResponse status: {e.response.status_code}"
            error_msg += f"\nResponse headers: {e.response.headers}"
            if e.response.content:
                error_msg += f"\nResponse body: {e.response.content.decode()}"
        raise Exception(error_msg)
    except Exception as e:
        raise Exception(f"Error downloading file: {str(e)}")

def test_box_client():
    """Test function for Box client"""
    # Sample token data
    test_token = {
        "read": {
            "access_token": "test_read_token",
            "expires_in": 3600,
            "token_type": "bearer"
        },
        "write": {
            "access_token": "test_write_token",
            "expires_in": 3600,
            "token_type": "bearer"
        }
    }
    
    try:
        # Test token parsing
        read_token = parse_token(test_token)
        print("\nToken parsing test:")
        print(f"Extracted read token: {read_token}")
        
        # Test with invalid token
        try:
            parse_token({"invalid": "token"})
            print("Error: Should have failed with invalid token")
        except Exception as e:
            print("Successfully caught invalid token error")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    test_box_client()
