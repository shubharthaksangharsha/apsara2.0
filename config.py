import json
import os

def create_config():
    config = {}
    print("Welcome to Apsara 2.0 Configuration Setup!")
    
    # LLM Provider
    print("\nSelect LLM Provider:")
    providers = ["Google", "OpenAI", "Local(Ollama)", "Claude", "HuggingFace", "Groq"]
    for i, provider in enumerate(providers, 1):
        print(f"{i}. {provider}")
    provider_choice = int(input("Enter the number of your choice: ")) - 1
    config['provider'] = providers[provider_choice]

    # Model selection based on provider
    if config['provider'] == "Google":
        models = ["gemini-1.5-flash", "gemini-1.5-pro-exp-0801", "gemini-1.5-pro", "gemini-1.0-pro"]
    elif config['provider'] == "Claude":
        models = ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
    elif config['provider'] == "Groq":
        models = [
            "llama-3.1-405b-reasoning", "llama-3.1-70b-versatile", "llama-3.1-8b-instant",
            "llama3-groq-70b-8192-tool-use-preview", "llama3-groq-8b-8192-tool-use-preview",
            "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it", "gemma2-9b-it"
        ]
    elif config['provider'] == "OpenAI":
        models = ["gpt-4", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"]
    elif config['provider'] == "Local(Ollama)":
        models = ["local-llm"]  # You might want to populate this with available local models
    elif config['provider'] == "HuggingFace":
        models = ["meta-llama/Meta-Llama-3-8B-Instruct"]  # Add more HuggingFace models as needed

    print("\nSelect Model:")
    for i, model in enumerate(models, 1):
        print(f"{i}. {model}")
    model_choice = int(input("Enter the number of your choice: ")) - 1
    config['model'] = models[model_choice]

    if config['provider'] == "Local(Ollama)":
        config['local_model'] = input("Enter the local model name: ")
    else:
        config['local_model'] = ""

    # Temperature
    config['temperature'] = float(input("Enter the temperature (0.0 to 1.0): "))
    
    # History
    config['history'] = input("Use conversation history? (y/n): ").lower() == 'y'
    if config['history']:
        config['history_size'] = int(input("Enter history size: "))
    
    # Tools
    print("\nAvailable tools:")
    tools = ["Search", "Gmail", "Finance", "Location", "Weather", "File Operations", "Shell", "Date and Time", "Media", "System", "Volume Control", "Python", "Knowledge", "Bluetooth", "WhatsApp", "Alarm", "Screenshare", "Note Taking", "To-Do List", "Playwright"]
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool}")
    print("Enter tool numbers separated by spaces, or 'all' for all tools.")
    tool_choice = input("Your choice: ")
    if tool_choice.lower() == 'all':
        config['tools'] = tools
    else:
        selected_tools = [tools[int(i) - 1] for i in tool_choice.split()]
        config['tools'] = selected_tools
    
    # Agent
    config['agent'] = input("Use Agent functionality? (y/n): ").lower() == 'y'
    
    # Voice
    config['voice'] = input("Use Voice Assistant? (y/n): ").lower() == 'y'
    
    # Save configuration
    with open('config.txt', 'w') as f:
        json.dump(config, f, indent=2)
    print("Configuration saved to config.txt")

def load_config():
    if os.path.exists('config.txt'):
        with open('config.txt', 'r') as f:
            return json.load(f)
    else:
        print("Config file not found. Creating a new configuration.")
        create_config()
        return load_config()

if __name__ == "__main__":
    create_config()
