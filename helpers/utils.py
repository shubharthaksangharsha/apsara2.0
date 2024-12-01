import streamlit as st

def add_export_button():
    import pandas as pd
    if 'messages' in st.session_state:
        df = pd.DataFrame(st.session_state.messages)
        st.download_button(
            label="Export Chat",
            data=df.to_csv(index=False),
            file_name='chat_history.csv',
            mime='text/csv',
        )

def get_models(provider):
    if provider == "Google":
        return ["gemini-1.5-flash", "gemini-1.5-flash-8b","gemini-1.5-flash-002","gemini-1.5-pro-002", "gemini-exp-1121","gemini-exp-1114","gemini-1.5-pro-exp-0801", "gemini-1.5-pro",  "gemini-1.0-pro"]
    elif provider == "Claude":
        return ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
    elif provider == "Groq":
        return [
            "llama-3.2-90b-vision-preview", "llama-3.2-11b-vision-preview", "llama-3.1-405b-reasoning", "llama-3.1-70b-versatile", "llama-3.1-8b-instant",
            "llama-3.2-1b-preview", "llama-3.2-3b-preview", 
            "llama3-groq-70b-8192-tool-use-preview", "llama3-groq-8b-8192-tool-use-preview",
            "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it", "gemma2-9b-it", 
            "llava-v1.5-7b-4096-preview", 
        ]
    elif provider == "OpenAI":
        return ["gpt-4", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"]
    elif provider == "Local(Ollama)":
        return ["local-llm"]  # You might want to populate this with available local models
    elif provider == "HuggingFace":
        return ["meta-llama/Meta-Llama-3-8B-Instruct"]  # Add more HuggingFace models as needed
    else:
        return []

def get_available_tools():
    return ["Search", "Gmail", "Finance", "Location", "Weather", "File Operations", "Shell", "Date and Time", "Media", "System", "Volume Control", "Python", "Knowledge", "Bluetooth", "WhatsApp", "Alarm", "Screenshare", "Note Taking", "To-Do List"]

def generate_response(user_input, session_state):
    import streamlit as st
    from langchain_community.callbacks.streamlit.streamlit_callback_handler import StreamlitCallbackHandler
    st_callback = StreamlitCallbackHandler(st.container())

    if session_state.use_agent and session_state.agent:
        response = session_state.agent.invoke({"input": user_input}, {"callbacks": [st_callback]})
        answer = response['output']
    else:
        response = session_state.chain.invoke(user_input)
        answer = response['response']
    return answer

def log_chat(user_input, answer):
    with open('chats.txt', 'a') as f:
        f.write(f'\nHuman: {user_input}\n')
        f.write(f'AI: {answer}\n')