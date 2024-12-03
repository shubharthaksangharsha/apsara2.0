import argparse
import os
from dotenv import load_dotenv
import warnings
import json
from config import initialize_env, create_config
import sys

# Import helper functions
from helpers.llm import get_llm
from helpers.agent import create_agent, update_llm_and_chain, initialize_session_state
from helpers.voice import voice_assistant, takeCommand, speak, transcribe_audio, cli_voice_assistant
from helpers.utils import generate_response, get_models, get_available_tools

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
        print(f"Error logging chat: {str(e)}")

def initialize_cli_config():
    """Initialize configuration for CLI"""
    try:
        # Load configuration from config.txt
        with open('config.txt', 'r') as f:
            saved_config = json.load(f)
        
        # Convert the saved config to our CLI format
        config = {
            'use_agent': saved_config.get('agent', False),  # Use the 'agent' key from saved config
            'use_voice': saved_config.get('voice', False),
            'provider': saved_config.get('provider', "Google"),
            'model': saved_config.get('model'),
            'temperature': saved_config.get('temperature', 0.5),
            'use_history': saved_config.get('history', True),
            'history_size': saved_config.get('history_size', 5),
            'selected_tools': saved_config.get('tools', [])  # Use the 'tools' key from saved config
        }
        
        return config
        
    except (FileNotFoundError, json.JSONDecodeError):
        # If config file doesn't exist or is invalid, return default config
        config = {
            'use_agent': False,
            'use_voice': False,
            'provider': "Google",
            'model': None,
            'temperature': 0.5,
            'use_history': True,
            'history_size': 5,
            'selected_tools': []
        }
        
        # Set default model based on provider
        models = get_models(config['provider'])
        config['model'] = models[0] if models else None
        
        return config

def cli_interface(config):
    """Command Line Interface for the assistant"""
    print("\nWelcome to Apsara 2.0 CLI - Advanced AI Assistant")
    print("------------------------------------------------")
    print(f"Current Configuration:")
    print(f"LLM Provider: {config['provider']}")
    print(f"Model: {config['model']}")
    print(f"Agent Mode: {'Enabled' if config['use_agent'] else 'Disabled'}")
    print(f"Voice Mode: {'Enabled' if config['use_voice'] else 'Disabled'}")
    print("------------------------------------------------")
    print("Commands:")
    print("- 'exit' or 'quit' or 'bye': Exit the program")
    print("- 'config': Change settings")
    print("- 'voice': Toggle voice mode")
    print("------------------------------------------------")

    # Initialize LLM
    llm = get_llm(temperature=config['temperature'], 
                  provider=config['provider'], 
                  model=config['model'])
    
    # Initialize memory with different keys based on agent/chain
    from langchain.memory import ConversationBufferWindowMemory
    if config['use_agent']:
        memory = ConversationBufferWindowMemory(k=config['history_size'], 
                                              return_messages=True, 
                                              memory_key='chat_history')
    else:
        memory = ConversationBufferWindowMemory(k=config['history_size'],
                                              return_messages=True,
                                              memory_key='chat_history')
    
    # Initialize agent or chain
    if config['use_agent']:
        assistant = create_agent(llm, memory, config['selected_tools'])
    else:
        from helpers.llm import get_chain
        assistant = get_chain(llm, memory)

    while True:
        try:
            if config.get('use_voice', False):
                query = cli_voice_assistant(config['use_agent'])
                if query is None:
                    continue
                print(f"You said: {query}")
            else:
                query = input("\nYou: ").strip()

            # Check for exit commands first
            if query.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye! Thank you for using Apsara 2.0")
                return  # This will exit the cli_interface function
                
            if not query:  # Skip empty inputs
                continue
                
            if query.lower() == 'config':
                print("\nConfiguration Options:")
                use_agent = input("Use Agent (yes/no)? ").lower().startswith('y')
                
                # Update tools only if agent is enabled
                if use_agent:
                    available_tools = get_available_tools()
                    print("\nAvailable tools:")
                    for i, tool in enumerate(available_tools, 1):
                        print(f"{i}. {tool}")
                    
                    tool_input = input("\nEnter tool numbers to use (comma-separated, or 'all'): ").strip()
                    if tool_input.lower() == 'all':
                        config['selected_tools'] = available_tools
                    else:
                        try:
                            selected_indices = [int(i.strip()) - 1 for i in tool_input.split(',')]
                            config['selected_tools'] = [available_tools[i] for i in selected_indices if 0 <= i < len(available_tools)]
                        except (ValueError, IndexError):
                            print("Invalid input. No tools selected.")
                            config['selected_tools'] = []
                else:
                    config['selected_tools'] = []
                
                config['use_agent'] = use_agent
                config['use_voice'] = input("Use Voice (yes/no)? ").lower().startswith('y')
                
                # Reinitialize LLM and agent/chain based on new configuration
                llm = get_llm(temperature=config['temperature'], 
                              provider=config['provider'], 
                              model=config['model'])
                
                if config['use_agent']:
                    assistant = create_agent(llm, memory, config['selected_tools'])
                else:
                    from helpers.llm import get_chain
                    assistant = get_chain(llm, memory)
                
                continue
                
            if query.lower() == 'voice':
                config['use_voice'] = not config['use_voice']
                print(f"Voice mode {'enabled' if config['use_voice'] else 'disabled'}")
                continue

            # Generate response
            try:
                if config['use_agent']:
                    response = assistant.invoke({"input": query})
                    answer = response['output']
                else:
                    response = assistant.invoke({"question": query})
                    answer = response.get('response') or response.get('output', 'No response generated')
                
                print(f"\nAI: {answer}")
                
                # Log the conversation
                log_chat(query, answer)
                
                # Speak the response if voice mode is enabled
                if config.get('use_voice', False):
                    speak(answer)
                    
            except Exception as e:
                print(f"Error generating response: {str(e)}")

        except KeyboardInterrupt:
            print("\nOperation cancelled by user. Type 'exit' to quit.")
            continue
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            continue

def main():
    parser = argparse.ArgumentParser(description="Apsara 2.0 - Advanced AI Assistant")
    parser.add_argument("--gui", action="store_true", help="Launch the GUI version")
    parser.add_argument("--config", action="store_true", help="Create or modify configuration")
    args = parser.parse_args()

    if args.gui:
        # Launch Streamlit interface
        import subprocess
        subprocess.run(["streamlit", "run", "app.py"])
    else:
        try:
            # Launch CLI interface
            if args.config:
                create_config()
            config = initialize_cli_config()
            cli_interface(config)
        except KeyboardInterrupt:
            print("\nGoodbye! Thank you for using Apsara 2.0")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            sys.exit(0)  # Ensure the program exits cleanly

if __name__ == "__main__":
    main()