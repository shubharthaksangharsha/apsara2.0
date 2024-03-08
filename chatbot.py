#Langchain
from langchain.chains import ConversationChain, LLMChain
from langchain_community.chat_models import ChatOllama
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks import StreamingStdOutCallbackHandler


#agents modules
from langchain import hub 
from langchain.agents import AgentType, initialize_agent, load_tools,AgentExecutor,  create_structured_chat_agent
from agent_prompt import get_agent_prompt
from mytools import *
from my_music_tools import * 
from my_utility_tools import * 

#extra lib 
import sys 
import os
from time import sleep 
import warnings
import argparse

parser = argparse.ArgumentParser(description='A chatbot that can use either the Groq API or a local LLM model using Ollama and openchat to generate responses. The chatbot has two main functionalities: it can use agents that have real-time knowledge using search and other advanced tools, or it can use a normal chatbot.')
# Add the arguments
parser.add_argument('--agent', action='store_true', help='Use the agent functionality for real-time knowledge. Default is False', default=False)
parser.add_argument('--local', action='store_true', help='Use local LLM - Ollama(openchat) or Groq. True for local and False for Groq. Default is False', default=False)
parser.add_argument('--temp', action='store', help='Set the temperature for the LLM. Default is 0.0', default=0.0, type=float)
parser.add_argument('--hist', action='store_true', help='Set the history for the LLM. Default is 2 messages', default=False)

# Parse the arguments
args = parser.parse_args()

# Now you can use them
print('Temperature: ', args.temp)
if args.agent:
    print("Using agent")
else: 
    print("Using chain")

if args.local:
    print("Using local")
else:
     print("Using Groq")

print('Starting...')



# Suppress specific warnings
warnings.filterwarnings("ignore")

#Set Langsmith functionality on 
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Apsara 2.0"


#Create LLM
def get_llm(temperature=0.5, local=True, groq_api_key: str = None):
    if local:
        llm = ChatOllama(model='openchat', temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
    else:
        llm = ChatGroq(api_key=groq_api_key, max_tokens=32768, streaming=True, temperature=args.temp, 
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
    tools = load_tools(["serpapi", "llm-math"], llm=llm)
    tools.append(mylocation), tools.append(read_tool), tools.append(write_tool), tools.append(weather_tool)
    tools.append(python_tool), tools.append(get_today_date), tools.append(play_youtube)
    tools.append(find_phone), tools.append(check_battery), tools.append(open_spotify) 
    tools.append(play_spotify), tools.append(detect_spotify_device), tools.append(print_current_song_details)
    tools.append(pause_or_resume_spotify)
    tools.append(restart_laptop), tools.append(shutdown_laptop)
    tools.append(increase_volume), tools.append(decrease_volume), tools.append(mute_volume)
    
    
    if args.hist:    
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
        verbose=True, 
        handle_parsing_errors=True)
        return agent  
       
    
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
            response = agent.invoke({'input': query})
            with open('chats.txt', 'a') as f: 
                    f.writelines(f'\nHuman: {query}\n')
                    f.writelines(f'Agent: {response}\n')
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
    llm = get_llm(temperature=0.5, local=local, groq_api_key=api_key)
    chain = get_chain(llm=llm, memory=memory)
    agent = create_agent()
    chat(agent_complete_toggle=args.agent)
    
    