import argparse
import os
from dotenv import load_dotenv
import warnings
import json

# Langchain imports
from langchain.chains import ConversationChain, LLMChain
from langchain_community.chat_models import ChatOllama
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.callbacks import StreamingStdOutCallbackHandler

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

# Voice imports
import speech_recognition as sr
import pyaudio
import pvporcupine
import struct
from gtts import gTTS
import tempfile
from groq import Groq 


client = Groq()

# Load environment variables
load_dotenv()

# Suppress specific warnings
warnings.filterwarnings("ignore")

# Set Langsmith functionality on
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Apsara 2.0"

def get_llm(temperature=0.5, provider=None, model=None):
    if provider == "Local(Ollama)":
        return ChatOllama(model=model, temperature=temperature, streaming=True)
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
    if memory:
        print('memory', memory)
        return ConversationChain(llm=llm, memory=memory, prompt=prompt, input_key='question', verbose=False)
    else:
        print('no memory')
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
        "Playwright": playwright_tools,
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

def takeCommand(pause_threshold=1.5, timeout=5, phrase_time_limit=None):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = pause_threshold
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("Recognizing...")
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

def voice_assistant(agent, memory, chain, porcupine, audio_stream, use_agent):
    try:
        while True:
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
    parser = argparse.ArgumentParser(description="Apsara 2.0 - Advanced AI Assistant")
    parser.add_argument("--config", action="store_true", help="Create or modify configuration")
    args = parser.parse_args()

    if args.config or not os.path.exists('config.txt'):
        from config import create_config
        create_config()
    
    from config import load_config
    config = load_config()

    # Set up memory
    memory = ConversationBufferWindowMemory(k=config.get('history_size', 5), return_messages=True, memory_key='chat_history') if config.get('history', False) else ConversationBufferWindowMemory(k=1, return_messages=True, memory_key='chat_history')

    # Set up LLM
    llm = get_llm(temperature=config['temperature'], provider=config['provider'], model=config['model'])

    # Set up chain or agent
    if config.get('agent', False):
        agent = create_agent(llm, memory, config['tools'])
    else:
        chain = get_chain(llm=llm, memory=memory)

    # Voice assistant setup
    if config.get('voice', False):
        pico_key = os.environ.get('pico_key')
        porcupine = pvporcupine.create(access_key=pico_key, keyword_paths=['./apsara_keyword/ap-sara_en_linux_v2_2_0.ppn', './apsara_keyword/app-sara_en_linux_v2_2_0.ppn'])
        paudio = pyaudio.PyAudio()
        audio_stream = paudio.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)
        voice_assistant(agent if config.get('agent', False) else None, memory, chain if not config.get('agent', False) else None, porcupine, audio_stream, config.get('agent', False))
    else:
        # Text-based chat loop
        while True:
            user_input = input("You: ")
            if user_input.strip().lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            try:
                if config.get('agent', False):
                    response = agent.invoke({'input': user_input})
                    answer = response['output']
                else:
                    response = chain.invoke(user_input)
                    answer = response['response']
                print(f"AI: {answer}")
                with open('chats.txt', 'a') as f:
                    f.write(f'\nHuman: {user_input}\n')
                    f.write(f'AI: {answer}\n')
            except Exception as e:
                print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()