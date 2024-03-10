from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
from concurrent.futures import ThreadPoolExecutor
import re

CHUNK_SIZE = 500  # Number of characters per chunk

def chunk_text(text):
    """Split the text into chunks based on periods and perform additional cleaning."""
    # Split text into chunks based on periods
    chunks = text.split('.')
    
    # Remove leading and trailing whitespace, newline characters, and other unwanted characters
    cleaned_chunks = [re.sub(r'[\n\t]', '', chunk.strip()) for chunk in chunks]
    
    # Filter out empty or whitespace-only chunks
    cleaned_chunks = [chunk for chunk in cleaned_chunks if chunk]
    
    return cleaned_chunks


def speak_chunk(chunk, lang='en'):
    """Convert a chunk of text to speech and return the audio data."""
    mp3_fo = BytesIO()
    speech = gTTS(text=chunk, lang=lang, slow=False, lang_check=False)
    speech.write_to_fp(mp3_fo)
    mp3_fo.seek(0)
    return mp3_fo



def play_audio(audio_data):
    """Play the audio data."""
    audio_data.seek(0)  # Reset file position to the beginning
    audio = AudioSegment.from_mp3(audio_data)  # Use read() to get bytes-like object
    play(audio)

def speak(paragraph, lang='en'):
    """Process a big paragraph."""
    chunks = chunk_text(paragraph)
    chunks = [chunk for chunk in chunks if chunk.strip()]

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(speak_chunk, chunk, lang) for chunk in chunks]
        audio_data_list = [future.result() for future in futures]
    
    for audio_data in audio_data_list:
        play_audio(audio_data)


