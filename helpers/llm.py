from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama
from langchain_groq import ChatGroq
import os

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
    prompt = PromptTemplate(input_variables=['question'], template="""
    The following is a friendly conversation between a human and an AI. 
    The AI is talkative and provides lots of specific details from its context. 
    If the AI does not know the answer to a question, it truthfully says it does not know.
    
    {chat_history}
                                             
    Human: {question}
    AI:""")
    chain = ConversationChain(
        llm=llm, 
        memory=memory, 
        prompt=prompt, 
        input_key='question',
        verbose=False,
    )
    return chain
