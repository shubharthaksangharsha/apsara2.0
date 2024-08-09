import streamlit as st
import uuid
import os
from dotenv import load_dotenv
import warnings
import json

# Langchain imports
from langchain.chains import ConversationChain
from langchain_community.chat_models import ChatOllama
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.callbacks.streamlit.streamlit_callback_handler import StreamlitCallbackHandler

# Agent imports
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain_community.agent_toolkits.load_tools import load_tools
from agent_prompt import get_agent_prompt, get_agent_prompt_for_gemini

# Custom tool imports
from mytools import *
from my_music_tools import *
from my_utility_tools import *
from whatsapp_tool import *
from alarm_tools import *
from image_tools import *
from notes_tools import * 
from export_utils import add_export_button
from langchain.tools.human.tool import HumanInputRun

# Voice
import speech_recognition as sr
import pyaudio
import pvporcupine
import struct
from gtts import gTTS
import tempfile
import threading
from queue import Queue, Empty
from groq import Groq
from audio_recorder_streamlit import audio_recorder


# Load environment variables
load_dotenv()

# Suppress specific warnings
warnings.filterwarnings("ignore")

# Set Langsmith functionality on
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Apsara 2.0"


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

@st.cache_resource
def get_llm(temperature=0.5, provider=None, model=None):
    if provider == "Local(Ollama)":
        return ChatOllama(model=st.session_state.local_model, temperature=temperature, streaming=True)
    if provider == "HuggingFace":
        return HuggingFaceEndpoint(repo_id=model, max_new_tokens=2048, temperature=temperature)
    if provider == "OpenAI":
        return ChatOpenAI(model=model, temperature=temperature, streaming=True)
    if provider == "Claude":
        return ChatAnthropic(model=model, temperature=temperature, streaming=True)
    if provider == "Google":
        return ChatGoogleGenerativeAI(model=model, stream=True, api_key=os.environ.get('gemini'), temperature=temperature, convert_system_message_to_human=True, max_output_tokens=8192)
    if provider == "Groq":
        return ChatGroq(model=model, api_key=os.environ.get('groq'), streaming=True, temperature=temperature)
    
    # Default case
    return ChatGroq(model='llama3-70b-8192', api_key=os.environ.get('groq'), streaming=True, temperature=temperature)

def get_chain(llm=None, memory=None):
    prompt = PromptTemplate(input_variables=["question"], template="""
    The following is a friendly conversation between a human and an AI. 
    The AI is talkative and provides lots of specific details from its context. 
    If the AI does not know the answer to a question, it truthfully says it does not know.
    
    {chat_history}
                                             
    Human: {question}
    AI:""")
    return ConversationChain(llm=llm, memory=memory, prompt=prompt, input_key='question', verbose=False)

def create_agent(llm, memory, selected_tools):
    tools = []
    if "Search" in selected_tools:
        tools.extend(load_tools(["serpapi"], llm=llm))
    if "Gmail" in selected_tools:
        from gmail_tools import send_mail, search_google, get_thread, create_draft, get_message, get_gmail_ids, get_date, create_event, get_events
        tools.extend([send_mail, search_google, get_thread, create_draft, get_message, get_gmail_ids, get_date, create_event, get_events])
    
    custom_tools = {
        "Finance": yfinance_tool,
        "Location": mylocation,
        "Weather": weather_tool,
        "File Operations": file_tools,
        "Shell": shell_tool,
        "Date and Time": [get_today_date, get_current_time],
        "Media": play_youtube,
        "System": [restart_laptop, shutdown_laptop, check_battery],
        "Volume Control": [increase_volume, decrease_volume, mute_volume, umute_volume],
        "Python": python_tool,
        "Knowledge": internal_knowledge_tool,
        "Bluetooth": [connect_bluetooth_device, disconnect_bluetooth_device, bluetooth_available_devices, turn_on_bluetooth, turn_off_bluetooth],
        "WhatsApp": send_whatsapp_message,
        "Alarm": set_alarm_or_timer, 
        "Screenshare": screenshare_tool,
        "Note Taking": note_taking_tool,
        "To-Do List": to_do_list_tool,
    }
    
    for tool, tool_func in custom_tools.items():
        if tool in selected_tools:
            if isinstance(tool_func, list):
                tools.extend(tool_func)
            else:
                tools.append(tool_func)
    
    prompt = get_agent_prompt_for_gemini() if isinstance(llm, ChatGoogleGenerativeAI) else get_agent_prompt()
    agent = create_structured_chat_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=10, handle_parsing_errors=True, memory=memory)

def initialize_session_state():
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationBufferWindowMemory(k=5, return_messages=True, memory_key='chat_history')
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'use_agent' not in st.session_state:
        st.session_state.use_agent = True
    if 'use_voice' not in st.session_state:
        st.session_state.use_voice = False
    if 'stop_signal' not in st.session_state:
        st.session_state.stop_signal = False
    if 'uuid' not in st.session_state:
        st.session_state.uuid = str(uuid.uuid4())

def update_llm_and_chain():
    st.session_state.llm = get_llm(
        temperature=st.session_state.temperature,
        provider=st.session_state.llm_provider,
        model=st.session_state.model
    )
    st.session_state.chain = get_chain(llm=st.session_state.llm, memory=st.session_state.memory)
    if st.session_state.use_agent:
        st.session_state.agent = create_agent(st.session_state.llm, st.session_state.memory, st.session_state.selected_tools)
    else:
        st.session_state.agent = None

# Voice functions 
def takeCommand(pause_threshold=0.6, timeout=5, phrase_time_limit=8):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = pause_threshold
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
            return query
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Could you please repeat?")
            return "None"
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
                os.system('mpg123 wake_word.mp3')
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

def main():
    st.set_page_config(page_title='Apsara 2.0 - Advance AI Assistant',  layout='wide', initial_sidebar_state='auto')
    st.title("Apsara 2.0 - Advanced AI Assistant")
    
    initialize_session_state()
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    st.session_state.use_agent = st.sidebar.checkbox("Use Agent", value=True)
    st.session_state.use_voice = st.sidebar.checkbox("Use Voice Assistant", value=st.session_state.use_voice)
    
    # LLM Provider selection
    llm_providers = ["Google", "OpenAI", "Local(Ollama)", "Claude", "HuggingFace", "Groq"]
    st.session_state.llm_provider = st.sidebar.selectbox("LLM Provider", llm_providers, index=0)
    
    # Model selection based on provider
    if st.session_state.llm_provider == "Google":
        models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
    elif st.session_state.llm_provider == "Claude":
        models = ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
    elif st.session_state.llm_provider == "Groq":
        models = [
            "llama-3.1-405b-reasoning", "llama-3.1-70b-versatile", "llama-3.1-8b-instant",
            "llama3-groq-70b-8192-tool-use-preview", "llama3-groq-8b-8192-tool-use-preview",
            "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it", "gemma2-9b-it"
        ]
    elif st.session_state.llm_provider == "OpenAI":
        models = ["gpt-4", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"]
    elif st.session_state.llm_provider == "Local(Ollama)":
        models = ["local-llm"]  # You might want to populate this with available local models
    elif st.session_state.llm_provider == "HuggingFace":
        models = ["meta-llama/Meta-Llama-3-8B-Instruct"]  # Add more HuggingFace models as needed
    
    st.session_state.model = st.sidebar.selectbox("LLM Model", models, index=0)
    
    if st.session_state.llm_provider == "Local(Ollama)":
        st.session_state.local_model = st.sidebar.text_input("Local Model Name", value="")
    else:
        st.session_state.local_model = ""

    st.session_state.temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.001)
    st.session_state.use_history = st.sidebar.checkbox("Use History", value=True)
    st.session_state.history_size = st.sidebar.number_input("History Size (k):", min_value=1, max_value=50, value=5)
    
    # Update memory with the new history size
    st.session_state.memory.k = st.session_state.history_size
    
    # Tool selection
    st.sidebar.subheader("Select Tools")
    available_tools = ["Search", "Gmail", "Finance", "Location", "Weather", "File Operations", "Shell", "Date and Time", "Media", "System", "Volume Control", "Python", "Knowledge", "Bluetooth", "WhatsApp", "Alarm", "Screenshare", "Note Taking", "To-Do List"]
    if 'selected_tools' not in st.session_state:
        st.session_state.selected_tools = available_tools  # Select all tools by default

    col1, col2 = st.sidebar.columns(2)
    if col1.button("Select All"):
        st.session_state.selected_tools = available_tools
    if col2.button("Deselect All"):
        st.session_state.selected_tools = []
        
    st.session_state.selected_tools = st.sidebar.multiselect(
        "Choose tools to use:",
        available_tools,
        default=st.session_state.selected_tools
    )

    # Update button
    if st.sidebar.button("Update Configuration"):
        update_llm_and_chain()
        st.sidebar.success("Configuration updated!")

    # Initialize LLM and chain if not already done
    if 'llm' not in st.session_state or 'chain' not in st.session_state:
        update_llm_and_chain()

    # Chat interface
    st.subheader("Chat with Apsara 2.0")

    
    # Top right sidebar for current settings
    with st.sidebar:
        st.write("Current Settings:")
        st.write(f"LLM: {st.session_state.model}")
        st.write(f"Agent: {'On' if st.session_state.use_agent else 'Off'}")
        st.write(f"Voice Assistant: {'On' if st.session_state.use_voice else 'Off'}")
    
    # Voice Input 
    audio_bytes = audio_recorder(
        text="or",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="2x", 
        sample_rate=16000
    )
    
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    

    # Chat input
    user_input = st.chat_input("You:")
    
    

    if user_input or audio_bytes:
        print('audio_bytes', audio_bytes)
        print('user_input', user_input)
        st_callback = StreamlitCallbackHandler(st.container())
        if audio_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            try:
                with st.spinner("Transcribing..."):
                    user_input = transcribe_audio(tmp_file_path)
            except Exception as e:
                st.error(f"An error occurred during transcription: {str(e)}")
            finally:
                os.unlink(tmp_file_path)            
                del audio_bytes
        
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate AI response
        with st.chat_message("assistant"):
            response_container = st.empty()
            full_response = ""

            # Display "Thinking..." initially
            response_container.markdown("Thinking...")

            try:
                if st.session_state.use_agent and st.session_state.agent:
                    # Display "Entering new AgentExecutor chain..."
                    response_container.markdown("Entering new AgentExecutor chain...")

                    # Run the agent and capture the output
                    response = st.session_state.agent.invoke({"input": user_input}, 
                                                             {"callbacks": [st_callback]})
                    
                    print('RESPONSE:', response, type(response))
                    answer = response['output']
                else:
                    response = st.session_state.chain.invoke(user_input)
                    print('Chain response', response)
                    answer = response['response']
                
                # Update the response container with the final answer
                response_container.markdown(answer)
                
                # Add AI response to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Log chat
                with open('chats.txt', 'a') as f:
                    f.write(f'\nHuman: {user_input}\n')
                    f.write(f'AI: {answer}\n')
            except json.JSONDecodeError as e:
                st.error(f"Error parsing LLM output: {str(e)}")
                st.error("The LLM output was not in the expected format. Please try again or rephrase your query.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    

    
    # Display chat history
    if st.session_state.use_history:
        with st.expander("Chat History", expanded=False):
            st.text_area("History:", value=st.session_state.memory.buffer_as_str, height=300, disabled=True)
    
    
    st.markdown("---")  # Add a separator
    add_export_button()

    # Clear history button
    if st.button("Clear History"):
        st.session_state.memory.clear()
        st.session_state.messages = []
        st.success("Chat history cleared!")
        audio_bytes = None
    
        

    # Stop button
    if st.button("Stop Execution"):
        st.session_state.stop_signal = True
        st.success("Stop signal sent. Please wait for the current operation to halt.")

    # Voice Assistant
    if st.session_state.use_voice:
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

if __name__ == "__main__":
    main()