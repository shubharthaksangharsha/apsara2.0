import speech_recognition as sr
import os
import tempfile
from gtts import gTTS
import struct
import threading
from queue import Queue, Empty
import pyaudio
import pvporcupine
from groq import Groq
from audio_recorder_streamlit import audio_recorder

def transcribe_audio(audio_file):
    client = Groq()
    with open(audio_file, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="distil-whisper-large-v3-en",
            response_format="json",
            language='en'
        )
    print('TRANSCRIPTION:', transcription)
    return transcription.text

def takeCommand(pause_threshold=1.5, timeout=5, phrase_time_limit=None):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = pause_threshold
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("Recognizing...")
             # Save audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                wav_data = audio.get_wav_data()
                tmp_file.write(wav_data)
                tmp_file_path = tmp_file.name
            
            # Use Groq's Whisper for transcription
            query = transcribe_audio(tmp_file_path)
            
            # Clean up the temporary file
            os.unlink(tmp_file_path)
            
            print(f"User said: {query}\n")
            return query
        except sr.RequestError:
            print("Sorry, there was an error with the speech recognition service.")
            return "None"
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return "None"

def speak(text):
    tts = gTTS(text=text, lang='en', slow=False, lang_check=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        tts.save(temp_file.name)
        os.system(f'mpg123 {temp_file.name}')
    os.unlink(temp_file.name)

def voice_assistant(agent, memory, chain, porcupine, audio_stream, use_agent, queue):
    stop_signal = False
    try:
        while not stop_signal:
            # Check if there's a stop signal in the queue
            try:
                stop_signal = queue.get_nowait()
            except Empty:
                pass            
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)
            if keyword_index >= 0:
                os.system('mpg123 ./apsara_keyword/wake_word.mp3')
                query = takeCommand()
                if query == "None":
                    continue
                if 'exit' in query.lower() or 'bye' in query.lower():
                    speak("Goodbye!")
                    break
                try:
                    if use_agent:
                        response = agent.invoke({'input': query})
                        answer = response['output']
                    else:
                        response = chain.invoke(query)
                        answer = response['response']
                    speak(answer)
                    with open('chats.txt', 'a') as f:
                        f.write(f'\nHuman: {query}\n')
                        f.write(f'AI: {answer}\n')
                except Exception as e:
                    print(f"Error processing query: {str(e)}")
                    speak("I'm sorry, I couldn't process that. Please try again.")
    except Exception as e:
        print(f"Error in voice assistant: {str(e)}")
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        porcupine.delete()

def manage_voice_assistant():
    import streamlit as st
    from helpers.voice import speak, voice_assistant
    from queue import Queue
    import pvporcupine
    import pyaudio
    import os
    import threading

    if 'voice_assistant_active' not in st.session_state:
        st.session_state.voice_assistant_active = False
        st.session_state.voice_queue = Queue()

    if not st.session_state.voice_assistant_active:
        if st.button("Start Voice Assistant"):
            st.session_state.voice_assistant_active = True
            pico_key = os.environ.get('pico_key')
            porcupine = pvporcupine.create(access_key=pico_key, keyword_paths=['./apsara_keyword/ap-sara_en_linux_v2_2_0.ppn', './apsara_keyword/app-sara_en_linux_v2_2_0.ppn'])
            paudio = pyaudio.PyAudio()
            audio_stream = paudio.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)
            
            # Start voice assistant in a separate thread
            thread = threading.Thread(target=voice_assistant, args=(st.session_state.agent, st.session_state.memory, st.session_state.chain, porcupine, audio_stream, st.session_state.use_agent, st.session_state.voice_queue), daemon=True)
            thread.start()
            
            st.success("Voice Assistant started. Say 'Apsara' to activate.")
    else:
        st.warning("Voice Assistant is active. Say 'Apsara' to activate.")

    # Add a stop button for the voice assistant
    if st.button("Stop Voice Assistant"):
        st.session_state.voice_queue.put(True)
        st.session_state.voice_assistant_active = False
        st.success("Voice Assistant stopped.")

def process_audio_input(audio_bytes):
    import streamlit as st
    import tempfile
    import os
    from helpers.voice import transcribe_audio

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_file_path = tmp_file.name
    try:
        with st.spinner("Transcribing..."):
            user_input = transcribe_audio(tmp_file_path)
    except Exception as e:
        st.error(f"An error occurred during transcription: {str(e)}")
        user_input = ""
    finally:
        os.unlink(tmp_file_path)            
    return user_input