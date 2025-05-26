# Placeholder for GPT keyword extraction logic

import os
from openai import OpenAI
from dotenv import load_dotenv

def get_openai_client():
    """Get an OpenAI client instance with the API key."""
    # Load environment variables when needed
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return OpenAI(api_key=api_key)

def generate_summary(text):
    """
    Generate a 2-4 sentence summary of the transcript using GPT-4.
    
    Args:
        text (str): The transcript text to summarize
        
    Returns:
        str: A concise summary of the transcript
    """
    try:
        # Initialize client when needed
        client = get_openai_client()
        
        # Create the prompt for GPT-4
        prompt = f"""Please provide a concise 2-4 sentence summary of this transcript. 
Focus on the main points and key information. Keep it clear and professional.

Transcript:
{text}"""

        # Call GPT-4 API
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a professional summarization expert. Create clear, concise summaries that capture the essential information in 2-4 sentences."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Lower temperature for more focused responses
        )
        
        # Extract and clean the summary
        summary = response.choices[0].message.content.strip()
        return summary
            
    except Exception as e:
        raise Exception(f"Failed to generate summary: {str(e)}")

def extract_keywords(text):
    """
    Extract 5-10 relevant keywords or phrases from the transcript text using GPT-4.
    
    Args:
        text (str): The transcript text to analyze
        
    Returns:
        list: A list of 5-10 relevant keywords or phrases
    """
    try:
        # Initialize client when needed
        client = get_openai_client()
        
        # Create the prompt for GPT-4
        prompt = f"""Please analyze this transcript and extract 5-10 most relevant keywords or phrases. 
Focus on specific, meaningful terms and proper nouns. Return only the keywords as a comma-separated list.

Transcript:
{text}"""

        # Call GPT-4 API
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a keyword extraction specialist. Extract only the most relevant and specific keywords or phrases. Return them as a comma-separated list without explanations or additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Lower temperature for more focused responses
        )
        
        # Extract and clean the keywords
        keywords_text = response.choices[0].message.content.strip()
        keywords = [k.strip() for k in keywords_text.split(',')]
        
        return keywords
            
    except Exception as e:
        raise Exception(f"Failed to extract keywords: {str(e)}")

def test_keyword_extraction():
    """Test function for keyword extraction and summary generation"""
    test_text = """Hello, my name is William Higgins. I am a manager in the Solutions Engineering Department at Box.com. 
    I hope you're having a great day. This is a test audio file to be able to run a voice transcription on this file. 
    It's actually pretty boring, but I can go on and tell you that I'm watching a movie right now called Bullet Train, 
    starring Brad Pitt. It's a very good movie. I have it on mute because I'm also listening to the Atlanta Braves 
    baseball game, the radio broadcast. So that's about all I have for now. So this is my test audio clip."""
    
    try:
        print("\n=== Testing Keyword Extraction ===")
        keywords = extract_keywords(test_text)
        print("\nExtracted Keywords:")
        for i, keyword in enumerate(keywords, 1):
            print(f"{i}. {keyword}")
            
        print("\n=== Testing Summary Generation ===")
        summary = generate_summary(test_text)
        print("\nGenerated Summary:")
        print(summary)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_keyword_extraction()
