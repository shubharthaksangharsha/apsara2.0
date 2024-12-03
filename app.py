import streamlit as st
import uuid
import os
import warnings
import json
from langchain_community.callbacks.streamlit.streamlit_callback_handler import StreamlitCallbackHandler
from dotenv import load_dotenv
import time

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

def show_chat_history():
    """Display chat history from the chats.txt file"""
    try:
        if os.path.exists('chats.txt'):
            with open('chats.txt', 'r') as f:
                history = f.read()
            if history.strip():
                st.text_area("Chat History", value=history, height=300, disabled=True)
            else:
                st.info("No chat history available.")
        else:
            st.info("No chat history file found.")
    except Exception as e:
        st.error(f"Error reading chat history: {str(e)}")

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

    # Always show Stop Execution button at the top
    if st.button("⏹️ Stop Execution", key="stop_top", type="primary"):
        # Set stop signal
        st.session_state.stop_signal = True
        # Cancel any ongoing operations
        if 'current_operation' in st.session_state:
            st.session_state.current_operation = None
        # Reset voice-related states
        if 'voice_assistant_active' in st.session_state:
            st.session_state.voice_assistant_active = False
        if 'audio_recorder_state' in st.session_state:
            del st.session_state.audio_recorder_state
        # Clear any pending audio
        st.session_state.last_audio_bytes = None
        st.success("✋ Execution stopped. All operations have been halted.")
        time.sleep(1)  # Brief pause to show the message
        st.rerun()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_input = st.chat_input("You:")

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

    # Process input only if there's new input and no stop signal
    if (user_input or (audio_bytes and audio_bytes != st.session_state.get('last_audio_bytes'))) and not st.session_state.stop_signal:
        # Check if we just cleared history
        if getattr(st.session_state, 'just_cleared', False):
            st.session_state.just_cleared = False
            return
        
        st_callback = StreamlitCallbackHandler(st.container())
        
        # Prioritize text input over audio input
        if user_input:
            processed_input = user_input
            # Clear any pending audio input
            st.session_state.last_audio_bytes = audio_bytes  # Mark current audio as processed
        elif audio_bytes:
            with st.spinner("Transcribing audio..."):
                processed_input = process_audio_input(audio_bytes)
                st.session_state.last_audio_bytes = audio_bytes
        
        # Immediately display user input
        st.session_state.messages.append({"role": "user", "content": processed_input})
        with st.chat_message("user"):
            st.markdown(processed_input)
        
        # Generate AI response
        with st.chat_message("assistant"):
            response_container = st.empty()
            response_container.markdown("Thinking...")

            try:
                # Set current operation
                st.session_state.current_operation = "processing_input"
                
                # Process input with stop check
                answer = generate_response(processed_input, st.session_state)
                
                # Clear operation on success
                st.session_state.current_operation = None
                st.session_state.stop_signal = False
                
                response_container.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                log_chat(processed_input, answer)
            except json.JSONDecodeError as e:
                st.error(f"Error parsing LLM output: {str(e)}")
                st.error("The LLM output was not in the expected format. Please try again or rephrase your query.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.session_state.current_operation = None
                st.session_state.stop_signal = False

        # Reset stop signal after processing
        st.session_state.stop_signal = False
        st.rerun()

    # Add other buttons after the chat
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        add_export_button()
    
    with col2:
        # Toggle button label based on current state
        button_label = "Hide History" if st.session_state.show_history_state else "Show History"
        
        if st.button(button_label):
            st.session_state.show_history_state = not st.session_state.show_history_state
            st.rerun()
        
        # Only show history if state is True
        if st.session_state.show_history_state:
            show_chat_history()
    
    with col3:
        if st.button("Clear History"):
            # Clear everything related to chat and audio
            st.session_state.memory.clear()
            st.session_state.messages = []
            st.session_state.last_audio_bytes = None
            
            # Force clear all audio-related states
            if 'audio_recorder_state' in st.session_state:
                del st.session_state.audio_recorder_state
            if 'audio_bytes' in st.session_state:
                del st.session_state.audio_bytes
            if 'voice_assistant_active' in st.session_state:
                st.session_state.voice_assistant_active = False
            
            # Also clear the chats.txt file
            if os.path.exists('chats.txt'):
                open('chats.txt', 'w').close()
                
            st.session_state.just_cleared = True                
            st.success("Chat history cleared!")
            st.experimental_rerun()

    # Voice Assistant
    if st.session_state.use_voice:
        manage_voice_assistant()

if __name__ == "__main__":
    main()