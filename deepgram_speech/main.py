import os
from dotenv import load_dotenv
import speech_recognition as sr
from speech_to_text import * 
from text_to_speech import * 

if __name__ == "__main__":
    user_input = input("Press enter to start transcription: ")
    if user_input.lower() == "":
        result_transcript = transcript_me()
        if result_transcript:
            print("\n\nOverall Transcript:")
            print(result_transcript)
            text2speech(result_transcript)
        else:
            print("\n\nTranscription failed.")