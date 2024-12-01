import streamlit as st
import uuid
import os
import warnings
import json
from langchain_community.callbacks.streamlit.streamlit_callback_handler import StreamlitCallbackHandler
from dotenv import load_dotenv

# Import configurations
from config import initialize_env

# Import helper functions
from helpers.llm import get_llm
from helpers.agent import create_agent, update_llm_and_chain, initialize_session_state
from helpers.voice import voice_assistant, takeCommand, speak, process_audio_input, audio_recorder, transcribe_audio, manage_voice_assistant
from helpers.utils import add_export_button, generate_response, get_models, get_available_tools

# Import tools
from tools import *

# Load environment variables and suppress warnings
initialize_env()

def log_chat(user_input, answer):
    """Log chat messages to a file"""
    try:
        with open('chats.txt', 'a') as f:
            f.write(f'\nHuman: {user_input}\n')
            f.write(f'AI: {answer}\n')
    except Exception as e:
        st.error(f"Error logging chat: {str(e)}")

def main():
    st.set_page_config(page_title='Apsara 2.0 - Advanced AI Assistant', layout='wide', initial_sidebar_state='auto')
    st.title("Apsara 2.0 - Advanced AI Assistant")
    
    initialize_session_state()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        st.session_state.use_agent = st.checkbox("Use Agent", value=True)
        st.session_state.use_voice = st.checkbox("Use Voice Assistant", value=st.session_state.use_voice)
        
        # LLM Provider selection
        llm_providers = ["Google", "OpenAI", "Local(Ollama)", "Claude", "HuggingFace", "Groq"]
        st.session_state.llm_provider = st.selectbox("LLM Provider", llm_providers, index=0)
        
        # Model selection based on provider
        models = get_models(st.session_state.llm_provider)
        st.session_state.model = st.selectbox("LLM Model", models, index=0)
        
        if st.session_state.llm_provider == "Local(Ollama)":
            st.session_state.local_model = st.text_input("Local Model Name", value="")
        else:
            st.session_state.local_model = ""
        
        st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, 0.001)
        st.session_state.use_history = st.checkbox("Use History", value=True)
        st.session_state.history_size = st.number_input("History Size (k):", min_value=1, max_value=50, value=5)
        
        # Update memory with the new history size
        st.session_state.memory.k = st.session_state.history_size
        
        # Tool selection
        available_tools = get_available_tools()
        st.subheader("Select Tools")
        
        if 'selected_tools' not in st.session_state:
            st.session_state.selected_tools = available_tools
        
        col1, col2 = st.columns(2)
        if col1.button("Select All"):
            st.session_state.selected_tools = available_tools
        if col2.button("Deselect All"):
            st.session_state.selected_tools = []
        
        st.session_state.selected_tools = st.multiselect(
            "Choose tools to use:",
            available_tools,
            default=st.session_state.selected_tools
        )
        
        # Update button
        if st.button("Update Configuration"):
            update_llm_and_chain()
            st.success("Configuration updated!")

    # Initialize LLM and chain if not already done
    if 'llm' not in st.session_state or 'chain' not in st.session_state:
        update_llm_and_chain()

    # Chat interface
    st.subheader("Chat with Apsara 2.0")

    # Display current settings
    with st.sidebar:
        st.write("Current Settings:")
        st.write(f"LLM: {st.session_state.model}")
        st.write(f"Agent: {'On' if st.session_state.use_agent else 'Off'}")
        st.write(f"Voice Assistant: {'On' if st.session_state.use_voice else 'Off'}")

    # Voice Input
    try:
        audio_bytes = audio_recorder(
            text="or",
            recording_color="#e8b62c",
            neutral_color="#6aa36f",
            icon_name="microphone",
            icon_size="2x",
            sample_rate=16000
        )
    except Exception as e:
        st.error(f"Error recording audio: {str(e)}")
        audio_bytes = None

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_input = st.chat_input("You:")

    if user_input or audio_bytes:
        st_callback = StreamlitCallbackHandler(st.container())
        if audio_bytes:
            user_input = process_audio_input(audio_bytes)
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate AI response
        with st.chat_message("assistant"):
            response_container = st.empty()
            response_container.markdown("Thinking...")

            try:
                answer = generate_response(user_input, st.session_state)
                response_container.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                log_chat(user_input, answer)
            except json.JSONDecodeError as e:
                st.error(f"Error parsing LLM output: {str(e)}")
                st.error("The LLM output was not in the expected format. Please try again or rephrase your query.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Display chat history
    if st.session_state.use_history:
        with st.expander("Chat History", expanded=False):
            st.text_area("History:", value=st.session_state.memory.buffer_as_str, height=300, disabled=True)

    st.markdown("---")
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
        manage_voice_assistant()

if __name__ == "__main__":
    main()