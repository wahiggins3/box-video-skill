import os
import json
from whisper_client import transcribe_audio
from gpt_keywords import extract_keywords, generate_summary
from skills_formatter import format_metadata

def test_full_pipeline(audio_path):
    """
    Test the complete pipeline with a real audio file.
    
    Args:
        audio_path (str): Path to the audio file to test
    """
    print(f"\n=== Testing Full Pipeline with {audio_path} ===\n")
    
    try:
        # Step 1: Transcribe Audio
        print("1. Transcribing audio...")
        transcript_data = transcribe_audio(audio_path)
        print("\nTranscription successful!")
        print("\nFull Transcript:")
        print(transcript_data["text"])
        
        # Step 2: Extract Keywords
        print("\n2. Extracting keywords...")
        keywords = extract_keywords(transcript_data["text"])
        print("\nExtracted Keywords:")
        for i, keyword in enumerate(keywords, 1):
            print(f"{i}. {keyword}")
        
        # Step 3: Generate Summary
        print("\n3. Generating summary...")
        summary = generate_summary(transcript_data["text"])
        print("\nGenerated Summary:")
        print(summary)
        
        # Step 4: Format Box Skills Metadata
        print("\n4. Formatting Box Skills metadata...")
        metadata = format_metadata(transcript_data, keywords, summary)
        
        # Save results to a file
        output_file = "test_results.json"
        with open(output_file, "w") as f:
            json.dump({
                "transcript_data": transcript_data,
                "keywords": keywords,
                "summary": summary,
                "box_skills_metadata": metadata
            }, f, indent=2)
        
        print(f"\nResults saved to {output_file}")
        print("\nBox Skills Metadata Preview:")
        print(json.dumps(metadata, indent=2))
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")

def main():
    # Check if test audio file exists
    test_file = "test_audio.m4a"
    
    if not os.path.exists(test_file):
        print(f"\nError: Test file '{test_file}' not found!")
        print("\nPlease ensure you have a test audio file in one of these formats:")
        print("- test_audio.m4a")
        print("- test_audio.mp3")
        print("- test_audio.mp4")
        print("- test_audio.wav")
        return
    
    # Run the full pipeline test
    test_full_pipeline(test_file)

if __name__ == "__main__":
    main() 