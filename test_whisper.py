from whisper_client import transcribe_audio
import os

def test_transcription():
    # Test file path - you can replace this with your own audio file
    test_file = "test_audio.m4a"
    
    if not os.path.exists(test_file):
        print(f"Please place a test audio file named '{test_file}' in the current directory")
        return
    
    print("Starting transcription...")
    try:
        result = transcribe_audio(test_file)
        print("\nTranscription successful!")
        print("\nFull Text:")
        print(result["text"])
        print("\nSegments with timestamps:")
        for segment in result["segments"]:
            print(f"\nStart: {segment['start']:.2f}s")
            print(f"End: {segment['end']:.2f}s")
            print(f"Text: {segment['text']}")
    except Exception as e:
        print(f"Error during transcription: {str(e)}")

if __name__ == "__main__":
    test_transcription() 