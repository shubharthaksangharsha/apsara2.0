#Langchain
from langchain.chains import ConversationChain, LLMChain
from langchain_community.chat_models import ChatOllama
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks import StreamingStdOutCallbackHandler, StdOutCallbackHandler
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

from mytools import *
from my_music_tools import * 
from my_utility_tools import * 
from whatsapp_tool import * 
from alarm_tools import * 

#agents modules
from langchain import hub 
from langchain.agents import AgentType, initialize_agent, load_tools,AgentExecutor,  create_structured_chat_agent
from agent_prompt import get_agent_prompt, get_agent_prompt_for_gemini
from langchain.tools.render import render_text_description_and_args


#extra lib 
import sys 
import os
from time import sleep 
import warnings
import argparse

#voice 
from gtts_audio import speak
import speech_recognition as sr
import pvporcupine
import pyaudio
import struct 

#Load environment variables 
load_dotenv()

parser = argparse.ArgumentParser(description='''

Apsara 2.0: Advanced AI assistant project utilizing cloud-sourced LLM models or local options. Seamlessly switch between real-time knowledge access via agents (Enjoy additional functionalities like playing songs and more through agents for an enhanced user experience.) or traditional chatbot interactions. Customize LLM models and enable features such as voice input and Gmail tools integration for enhanced functionality.''')
# Add the arguments
parser.add_argument('--agent', action='store_true', help='Use the agent functionality for real-time knowledge. Default is False', default=False)
parser.add_argument('--local', action='store', help='Which LLM model to use(openchat/mistral/mixtral/your-model-name). Make sure you installed ollama and ollama-server is running.', default='', type=str)
parser.add_argument('--model', action='store', help='Which LLM model to use(groq/gpt4/gpt3.5/claude3-opus/claude3-haiku/claude3-sonnet/gemini-pro). Note: for gemini-pro use --hist is necessary. Default is Groq', default='groq', type=str)
parser.add_argument('--hugging', action='store_true', help='Use Hugging Face Mixtral Model. Default is False', default=False)
parser.add_argument('--temp', action='store', help='Set the temperature for the LLM [0.0-1.0]. Default is 0.001(to avoid 1e7 value)', default=0.001, type=float)
parser.add_argument('--hist', action='store_true', help='Set the history for the LLM. Default is False', default=False)
parser.add_argument('--voice', action='store', help='Activate voice input by saying Apsara by passing on/off. Default is off', default='off', type=str)
parser.add_argument('--gmail', action='store', help='Turn on/off Gmail tools for the LLM. Make sure you have credentials.json file. Default is off', default='off', type=str)


# Parse the arguments
args = parser.parse_args()


# Now you can use them
print('Temperature: ', args.temp)
print('Using Gmail: ', args.gmail)
if args.agent:
    print("Using agent")
else: 
    print("Using chain")

if args.local:
    print("Using local llm")
else:
    print('Using LLM:', args.model)

print('Starting...')

if args.gmail == 'on':
    from gmail_tools import * 



# Suppress specific warnings
warnings.filterwarnings("ignore")

#Set Langsmith functionality on 
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Apsara 2.0"


#Create LLM
def get_llm(temperature=0.5, local=True, groq_api_key: str = None):
    if args.local != '':
        llm = ChatOllama(model=args.local, temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
        return llm
    if args.hugging:
        llm = HuggingFaceEndpoint(repo_id='mistralai/Mixtral-8x7B-Instruct-v0.1',  max_new_tokens=2048)
        return llm                     
    if args.model == 'gpt3.5':
        llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
        return llm 
    if args.model == 'gpt4':
        llm = ChatOpenAI(model='gpt-4', temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
        return llm 
    if args.model == 'claude3-haiku':
       llm = ChatAnthropic(model='claude-3-haiku-20240307', temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
       return llm 
    if args.model == 'claude3-sonnet':
        llm = ChatAnthropic(model='claude-3-sonnet-20240229', temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
        return llm 
    if args.model == 'claude3-opus':
        llm = ChatAnthropic(model='claude-3-opus-20240229', temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
        return llm    
    if args.model == 'gemini-pro':
        llm = ChatGoogleGenerativeAI(model='gemini-pro', stream=True,api_key=os.environ.get('geminiv2'), temperature=temperature,convert_system_message_to_human=True, callbacks=[StdOutCallbackHandler()], max_output_tokens=2048)
        return llm 
    llm = ChatGroq(model = 'mixtral-8x7b-32768',api_key=groq_api_key,  streaming=True, temperature=args.temp, 
                       callbacks=[StreamingStdOutCallbackHandler()])
    return llm 

#Create Chain 
def get_chain(llm=None, memory=None):
    prompt = PromptTemplate(input_variables=["question"], template="""
        The following is a friendly conversation between a human and an AI. 
        The AI is talkative and provides lots of specific details from its context. 
        If the AI does not know the answer to a question, it truthfully says it does not know.
        
        {chat_history}
                                                 
        Human:{question}
        AI:""")
    chain = ConversationChain(llm=llm, memory=memory, prompt=prompt, input_key='question'
                              , verbose=False)
    return chain 

def clear_history():
    history = []

def create_agent():
    tools = load_tools(["llm-math", 'serpapi', 'wikipedia', 'human'], llm=llm)
    #Search tools 
    #tools.append(search_tool), 
    if args.gmail == 'on':
      #Gmail tools
      tools.append(send_mail), tools.append(search_google), tools.append(get_thread), tools.append(create_draft), 
      tools.append(get_message), tools.append(get_gmail_ids)
      #Calendar tools 
      tools.append(get_date), tools.append(create_event), tools.append(get_events)
    #Yahoo Finance Tool
    tools.append(yfinance_tool)
    #Weather tools
    tools.append(mylocation), tools.append(weather_tool)
    #Read and write tools
    # tools.append(read_tool), tools.append(write_save_tool), 
    #File tools 
    tools.extend(file_tools)
    #Shell tool 
    tools.append(shell_tool)
    #Playwright tool 
    tools.extend(playwright_tools)
    #Get today date and time tool
    tools.append(get_today_date), tools.append(get_current_time)
    #Play on youtube tool
    tools.append(play_youtube)
    #Utility tools 
    #TODO -> tools.append(find_or_ring_phone)
    tools.append(restart_laptop), tools.append(shutdown_laptop), tools.append(check_battery)
    tools.append(increase_volume), tools.append(decrease_volume), tools.append(mute_volume), tools.append(umute_volume)
    #Spotify tools 
    tools.append(open_spotify), tools.append(play_spotify), tools.append(detect_spotify_device), 
    tools.append(print_current_song_details), tools.append(pause_or_resume_spotify)
    tools.append(play_album_on_spotify), tools.append(play_artist_on_spotify)
    #Python tool
    tools.append(python_tool)
    #Internal Knowledge tool 
    #tools.append(internal_knowledge_tool) 
    
    #Bluetooth tools 
    tools.append(connect_bluetooth_device), tools.append(disconnect_bluetooth_device)
    tools.append(bluetooth_available_devices)
    tools.append(turn_on_bluetooth), tools.append(turn_off_bluetooth)

    #Whatsapp tool 
    tools.append(send_whatsapp_message)

    #Launch app tool 
    #tools.append(get_installed_applications)
    #tools.append(launch_app_tool)

    #Alarm/Timer tool 
    tools.append(set_alarm_or_timer)
    
    if args.hist:    
        if args.model == 'gemini-pro':
            prompt = get_agent_prompt_for_gemini()
        else:
            prompt = get_agent_prompt()
        agent =  create_structured_chat_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                                       max_iterations=10, handle_parsing_errors=True, memory=memory)
        return agent_executor
    else:
        agents = ["zero-shot-react-description", "conversational-react-description",
           "chat-zero-shot-react-description", "chat-conversational-react-description", 
           "structured-chat-zero-shot-react-description"]
        agent = initialize_agent(tools=tools, llm=llm, agent=AgentType(agents[-1]),
        max_iterations=100,
        verbose=True, 
        handle_parsing_errors=True,
        memory=memory)
        # agent.agent.llm_chain.prompt = agent_prompt #change the prompt #TODO
        # print(agent.agent.llm_chain.prompt) #view the prompt #TODO
        return agent  

#greeting function
def wishMe():
    '''
    This function greets the user based on the current time by playing an audio file using the os.system() method.

    Returns:
        None
    '''
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        os.system('mpg123 wish_me/good_morning.mp3')
    elif hour >= 12 and hour < 18:
        os.system('mpg123 wish_me/good_afternoon.mp3')
    else:
        os.system('mpg123 wish_me/good_evening.mp3')


#take voice command from the user microphone and convert it into text 
def takeCommand(pause_threshold = 0.6, timeout=5, phrase_time_limit=8):
    """
    This function listens to the user's voice input through the microphone and returns a string output.

    Args:
    pause_threshold (float): The minimum length of silence (in seconds) that is considered the end of a phrase.
    timeout (int): The maximum number of seconds that the function will wait for speech before timing out and returning.
    phrase_time_limit (int): The maximum number of seconds that this function will allow a phrase to continue before stopping and returning the first part of the speech recognized.

    Returns:
    str: The text of the speech recognized from the user's input.

    Raises:
    None
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = pause_threshold
        try:
            audio = r.listen(source,timeout=timeout,phrase_time_limit=phrase_time_limit)
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
        except Exception as e:
            print("Say that again please...")
            return "None"
    return query

def voice(agent_complete_toggle=True):
    '''
    This function is used to start the voice assistant.
    agent_complete_toggle: whether to use agent or not.
    '''
    if agent_complete_toggle:
        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)
            if keyword_index >= 0:
                os.system('mpg123 wake_word.mp3')
                query = takeCommand()
                if 'None' in query:
                    continue
                if 'exit' in query or 'bye' in query:
                        print('Okay bye...')
                        break
                try:
                    response = agent.invoke({'input': query})
                    
                    answer = response['output'] 
                    speak(answer)
                except Exception as e:
                    print(e)
                    print('Please try again')
                    pass
                with open('chats.txt', 'a') as f: 
                        f.writelines(f'\nHuman: {query}\n')
                        f.writelines(f'Agent: {answer}\n')
                print()  

    else: 
        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)
            if keyword_index >= 0:
                os.system('mpg123 wake_word.mp3')
                query = takeCommand()
                if 'None' in query:
                    continue
                if 'show_history' in query:
                    print(memory.buffer_as_str)
                    continue
                if 'exit' in query:
                    sys.exit()
                if 'clear_history' in query:
                    memory.clear()
                    print('Cleared history')
                    continue
                response = chain.invoke(query)    
                with open('chats.txt', 'a') as f: 
                        f.writelines(memory.buffer_as_str)
                print()           
    
def chat(agent_complete_toggle=True):
    if agent_complete_toggle:
        while True:
            query = input ('> ')
            if 'show_history' in query:
                print(memory.buffer_as_str)
                continue
            if 'exit' in query:
                    sys.exit()
            if 'clear_history' in query:
                memory.clear()
                print('Cleared history')
                continue
            print('Human: ', query)
            answer = None 
            try:
                response = agent.invoke({'input': query})
                answer = response['output']
            except Exception as e:
                print(e)
                print('Please try again')
                pass
            with open('chats.txt', 'a') as f: 
                    f.writelines(f'\nHuman: {query}\n')
                    f.writelines(f'Agent: {answer}\n')
            if args.hist:
                print('Printing History')
                print(memory.buffer_as_str)
            print()  

    else: 
        while True:
            query = input ('> ')
            if 'show_history' in query:
                print(memory.buffer_as_str)
                continue
            if 'exit' in query:
                sys.exit()
            if 'clear_history' in query:
                memory.clear()
                print('Cleared history')
                continue
            response = chain.invoke(query)    
            with open('chats.txt', 'a') as f: 
                    f.writelines(memory.buffer_as_str)
            print()        

if __name__ == '__main__':
    local = args.local
    api_key = os.environ.get('groq')
    memory = ConversationBufferWindowMemory(k=2, return_messages=True, memory_key='chat_history')
    llm = get_llm(temperature=args.temp, local=local, groq_api_key=api_key)
    chain = get_chain(llm=llm, memory=memory)
    agent = create_agent()
    
    if args.voice == 'on':
        porcupine = None
        audio_stream = None
        paudio = None
        pico_key = os.environ.get('pico_key')
        porcupine = pvporcupine.create(access_key = pico_key, keyword_paths=['./apsara_keyword/ap-sara_en_linux_v2_2_0.ppn','./apsara_keyword/app-sara_en_linux_v2_2_0.ppn'])
        paudio = pyaudio.PyAudio()
        audio_stream = paudio.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)
        voice(agent_complete_toggle=args.agent)
    else:
        chat(agent_complete_toggle=args.agent)
    
    
