import os
from dotenv import load_dotenv

from deepgram import (
    DeepgramClient,
    SpeakOptions,
)

load_dotenv()

def text2speech(text):
    """Records audio from the microphone, transcribes it to text, and then converts the text to speech using Deepgram."""
    try:
        SPEAK_OPTIONS = {"text": text}  # Use the recognized text
        filename = "output.wav"
        print('Text to speech:', text)
        # STEP 1 Create a Deepgram client using the API key from environment variables
        deepgram = DeepgramClient(api_key=os.getenv("DG_API_KEY"))

        # STEP 3 Configure the options (such as model choice, audio configuration, etc.)
        # models = ["aura-luna-en", "aura-athena-en"]
        options = SpeakOptions(
            model="aura-athena-en",
            encoding="linear16",
            container="wav"
        )

        # STEP 2 Call the save method on the speak property
        response = deepgram.speak.v("1").save(filename, SPEAK_OPTIONS, options)
        # print('Final response:', response)
        os.system('aplay output.wav')

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == '__main__':
    pass 