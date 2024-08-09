import streamlit as st
from audio_recorder_streamlit import audio_recorder
from groq import Groq
import os
import tempfile

# Initialize Groq client
client = Groq()

def transcribe_audio(audio_file):
    with open(audio_file, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3",
            response_format="json",
            language='en'
        )
    print('TRANSCRIPTION:', transcription)
    return transcription.text

st.title("Audio Recorder and Transcription App")

st.write("Click the microphone icon to start/stop recording.")

# Audio recorder
audio_bytes = audio_recorder(
    text="",
    recording_color="#e8b62c",
    neutral_color="#6aa36f",
    icon_name="microphone",
    icon_size="2x", 
    sample_rate=16000
)

def downgrade(file_name):
    text = f"ffmpeg \
  -i <your file> \
  -ar 16000 \
  -ac 1 \
  -map 0:a: \
  {tmp_file_path}"
    os.system(f'{text}')

if audio_bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_file_path = tmp_file.name
    
    
    try:
        downgrade(tmp_file_path)
        print('Done downgrading...')
        with st.spinner("Transcribing..."):
            transcription = transcribe_audio(tmp_file_path)
        st.write("Transcription:")
        st.write(transcription)
    except Exception as e:
        st.error(f"An error occurred during transcription: {str(e)}")
    finally:
        os.unlink(tmp_file_path)