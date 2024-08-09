import os
from dotenv import load_dotenv
import argparse
import warnings
from time import sleep
import sys

# Langchain imports
from langchain.chains import ConversationChain
from langchain_community.chat_models import ChatOllama
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Agent imports
from langchain.agents import AgentType, initialize_agent, create_structured_chat_agent, AgentExecutor
from langchain_community.agent_toolkits.load_tools import load_tools
from agent_prompt import get_agent_prompt, get_agent_prompt_for_gemini

# Custom tool imports
from mytools import *
from my_music_tools import *
from my_utility_tools import *
from whatsapp_tool import *
from alarm_tools import *

# Load environment variables
load_dotenv()

# Set up argument parser
parser = argparse.ArgumentParser(description='''
Apsara 2.0: Advanced AI assistant project utilizing cloud-sourced LLM models or local options. 
Seamlessly switch between real-time knowledge access via agents or traditional chatbot interactions. 
Customize LLM models and enable features such as Gmail tools integration for enhanced functionality.
''')

parser.add_argument('--agent', action='store_true', help='Use the agent functionality for real-time knowledge. Default is False', default=False)
parser.add_argument('--local', action='store', help='Which LLM model to use (openchat/mistral/mixtral/your-model-name). Make sure you installed ollama and ollama-server is running.', default='', type=str)
parser.add_argument('--model', action='store', help='Which LLM model to use (groq/gpt4/gpt3.5/claude3-opus/claude3-haiku/claude3-sonnet/gemini-pro). Default is Groq', default='groq', type=str)
parser.add_argument('--hugging', action='store_true', help='Use Hugging Face Mixtral Model. Default is False', default=False)
parser.add_argument('--temp', action='store', help='Set the temperature for the LLM [0.0-1.0]. Default is 0.001', default=0.001, type=float)
parser.add_argument('--hist', action='store_true', help='Set the history for the LLM. Default is False', default=False)
parser.add_argument('--gmail', action='store', help='Turn on/off Gmail tools for the LLM. Make sure you have credentials.json file. Default is off', default='off', type=str)

args = parser.parse_args()

# Print configuration
print('Temperature:', args.temp)
print('Using Gmail:', args.gmail)
print('Using agent' if args.agent else 'Using chain')
print('Using local llm' if args.local else f'Using LLM: {args.model}')

print('Starting...')

if args.gmail == 'on':
    from gmail_tools import *

# Suppress specific warnings
warnings.filterwarnings("ignore")

# Set Langsmith functionality on
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Apsara 2.0"

def get_llm(temperature=0.5, local=True, groq_api_key: str = None):
    if args.local != '':
        return ChatOllama(model=args.local, temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
    if args.hugging:
        return HuggingFaceEndpoint(repo_id="meta-llama/Meta-Llama-3-8B-Instruct", max_new_tokens=2048, temperature=args.temp)
    if args.model == 'gpt3.5':
        return ChatOpenAI(model='gpt-3.5-turbo', temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
    if args.model == 'gpt4':
        return ChatOpenAI(model='gpt-4', temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
    if args.model == 'claude3-haiku':
        return ChatAnthropic(model='claude-3-haiku-20240307', temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
    if args.model == 'claude3-sonnet':
        return ChatAnthropic(model='claude-3-sonnet-20240229', temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
    if args.model == 'claude3-opus':
        return ChatAnthropic(model='claude-3-opus-20240229', temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
    if args.model == 'gemini-pro':
        return ChatGoogleGenerativeAI(model='gemini-1.5-flash-latest', stream=True, api_key=os.environ.get('gemini'), temperature=temperature, convert_system_message_to_human=True, callbacks=[StreamingStdOutCallbackHandler()], max_output_tokens=4096)
    return ChatGroq(model='llama3-70b-8192', api_key=groq_api_key, streaming=True, temperature=args.temp, callbacks=[StreamingStdOutCallbackHandler()])

def get_chain(llm=None, memory=None):
    prompt = PromptTemplate(input_variables=["question"], template="""
    The following is a friendly conversation between a human and an AI. 
    The AI is talkative and provides lots of specific details from its context. 
    If the AI does not know the answer to a question, it truthfully says it does not know.
    
    {chat_history}
                                             
    Human: {question}
    AI:""")
    return ConversationChain(llm=llm, memory=memory, prompt=prompt, input_key='question', verbose=False)

def create_agent():
    tools = load_tools(["human", "serpapi"], llm=llm)
    if args.gmail == 'on':
        tools.extend([send_mail, search_google, get_thread, create_draft, get_message, get_gmail_ids, get_date, create_event, get_events])
    tools.extend([
        yfinance_tool, mylocation, weather_tool, *file_tools, shell_tool, get_today_date, get_current_time,
        play_youtube, restart_laptop, shutdown_laptop, check_battery, increase_volume, decrease_volume, 
        mute_volume, umute_volume, python_tool, internal_knowledge_tool, connect_bluetooth_device, 
        disconnect_bluetooth_device, bluetooth_available_devices, turn_on_bluetooth, turn_off_bluetooth,
        send_whatsapp_message, set_alarm_or_timer
    ])
    
    if args.hist:
        prompt = get_agent_prompt_for_gemini() if args.model == 'gemini-pro' else get_agent_prompt()
        agent = create_structured_chat_agent(llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=10, handle_parsing_errors=True, memory=memory)
    else:
        return initialize_agent(tools=tools, llm=llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                                max_iterations=100, verbose=True, handle_parsing_errors=True, memory=memory)

def chat(agent_complete_toggle=True):
    if agent_complete_toggle:
        while True:
            query = input('> ')
            if 'show_history' in query:
                print(memory.buffer_as_str)
                continue
            if 'exit' in query:
                print('Thank you for using me...')
                sys.exit()
            if 'clear_history' in query:
                memory.clear()
                print('Cleared history')
                continue
            print('Human:', query)
            try:
                response = agent.invoke({'input': query})
                answer = response['output']
                print('AI:', answer)
                with open('chats.txt', 'a') as f:
                    f.write(f'\nHuman: {query}\n')
                    f.write(f'AI: {answer}\n')
            except Exception as e:
                print('Error:', e)
                print('Please try again')
            if args.hist:
                print('Printing History')
                print(memory.buffer_as_str)
            print()
    else:
        while True:
            query = input('> ')
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
            print('AI:', response['response'])
            with open('chats.txt', 'a') as f:
                f.write(memory.buffer_as_str)
            print()

if __name__ == '__main__':
    api_key = os.environ.get('groq')
    memory = ConversationBufferWindowMemory(k=5, return_messages=True, memory_key='chat_history')
    llm = get_llm(temperature=args.temp, local=args.local, groq_api_key=api_key)
    chain = get_chain(llm=llm, memory=memory)
    agent = create_agent() if args.agent else None
    chat(agent_complete_toggle=args.agent)