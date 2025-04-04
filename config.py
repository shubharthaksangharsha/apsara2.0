import json
import os
from dotenv import load_dotenv
import warnings

def initialize_env():
    """Initialize environment variables and suppress warnings"""
    # Load environment variables
    load_dotenv()
    
    # Suppress warnings
    warnings.filterwarnings("ignore")
    
    # Set Langsmith functionality
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "Apsara 2.0"
    
    # Verify critical environment variables
    required_vars = [
        'OPENAI_API_KEY',
        'GOOGLE_API_KEY',
        'ANTHROPIC_API_KEY',
        'HUGGINGFACE_API_KEY',
        'GROQ_API_KEY',
        'SERPAPI_API_KEY',
        'pico_key'  # for voice wake word detection
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        warnings.warn(f"Missing environment variables: {', '.join(missing_vars)}")

def get_provider_models(provider):
    """Get available models for each provider"""
    models = {
        "Google": [
            "gemini-2.0-flash-thinking-exp-1219", 
            "gemini-2.0-flash-exp", 
            "gemini-exp-1206", 
            "gemini-1.5-flash",
            "gemini-1.5-pro-exp-0801",
            "gemini-1.5-pro",
            "gemini-1.0-pro"
        ],
        "Claude": [
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        "Groq": [
            "llama-3.1-405b-reasoning",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "llama3-groq-70b-8192-tool-use-preview",
            "llama3-groq-8b-8192-tool-use-preview",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768",
            "gemma-7b-it",
            "gemma2-9b-it"
        ],
        "OpenAI": [
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-4-turbo",
            "gpt-4-vision-preview"
        ],
        "Local(Ollama)": ["local-llm"],
        "HuggingFace": ["meta-llama/Meta-Llama-3-8B-Instruct"]
    }
    return models.get(provider, [])

def get_available_tools():
    """Get list of available tools"""
    return [
        "Search",
        "Gmail",
        "Finance",
        "Location",
        "Weather",
        "File Operations",
        "Shell",
        "Date and Time",
        "Media",
        "System",
        "Volume Control",
        "Python",
        "Knowledge",
        "Bluetooth",
        "WhatsApp",
        "Alarm",
        "Screenshare",
        "Note Taking",
        "To-Do List",
        "Playwright"
    ]

def create_config():
    """Create a new configuration file"""
    config = {}
    print("\n=== Welcome to Apsara 2.0 Configuration Setup! ===")
    
    # LLM Provider
    providers = ["Google", "OpenAI", "Local(Ollama)", "Claude", "HuggingFace", "Groq"]
    print("\nSelect LLM Provider:")
    for i, provider in enumerate(providers, 1):
        print(f"{i}. {provider}")
    
    while True:
        try:
            provider_choice = int(input("Enter the number of your choice: ")) - 1
            if 0 <= provider_choice < len(providers):
                config['provider'] = providers[provider_choice]
                break
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

    # Model selection
    models = get_provider_models(config['provider'])
    print("\nSelect Model:")
    for i, model in enumerate(models, 1):
        print(f"{i}. {model}")
    
    while True:
        try:
            model_choice = int(input("Enter the number of your choice: ")) - 1
            if 0 <= model_choice < len(models):
                config['model'] = models[model_choice]
                break
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

    # Local model name if applicable
    if config['provider'] == "Local(Ollama)":
        config['local_model'] = input("Enter the local model name: ")
    else:
        config['local_model'] = ""

    # Temperature
    while True:
        try:
            temp = float(input("\nEnter the temperature (0.0 to 1.0): "))
            if 0.0 <= temp <= 1.0:
                config['temperature'] = temp
                break
            print("Temperature must be between 0.0 and 1.0")
        except ValueError:
            print("Please enter a valid number.")

    # Agent setting (moved up before tools selection)
    config['agent'] = input("\nUse Agent functionality? (y/n): ").lower() == 'y'

    # Tools selection - only if agent is enabled
    if config['agent']:
        print("\nAvailable tools:")
        tools = get_available_tools()
        for i, tool in enumerate(tools, 1):
            print(f"{i}. {tool}")
        print("\nEnter tool numbers separated by spaces, or 'all' for all tools.")
        
        while True:
            tool_choice = input("Your choice: ").strip()
            if tool_choice.lower() == 'all':
                config['tools'] = tools
                break
            try:
                selected_indices = [int(i) - 1 for i in tool_choice.split()]
                if all(0 <= i < len(tools) for i in selected_indices):
                    config['tools'] = [tools[i] for i in selected_indices]
                    break
                print("Invalid tool number(s). Please try again.")
            except ValueError:
                print("Please enter valid numbers or 'all'.")
    else:
        # If agent is disabled, set tools to empty list
        config['tools'] = []

    # History settings
    config['history'] = input("\nUse conversation history? (y/n): ").lower() == 'y'
    if config['history']:
        while True:
            try:
                size = int(input("Enter history size (1-50): "))
                if 1 <= size <= 50:
                    config['history_size'] = size
                    break
                print("History size must be between 1 and 50")
            except ValueError:
                print("Please enter a valid number.")

    # Voice setting
    config['voice'] = input("Use Voice Assistant? (y/n): ").lower() == 'y'

    # Save configuration
    try:
        with open('config.txt', 'w') as f:
            json.dump(config, f, indent=2)
        print("\nConfiguration saved successfully to config.txt")
    except Exception as e:
        print(f"\nError saving configuration: {str(e)}")

def load_config():
    """Load configuration from file or create new if not exists"""
    try:
        if os.path.exists('config.txt'):
            with open('config.txt', 'r') as f:
                return json.load(f)
        else:
            print("Config file not found. Creating a new configuration.")
            create_config()
            return load_config()
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        print("Creating new configuration...")
        create_config()
        return load_config()

def get_default_config():
    """Get default configuration settings"""
    return {
        'provider': 'Google',
        'model': 'gemini-1.5-pro',
        'local_model': '',
        'temperature': 0.7,
        'history': True,
        'history_size': 5,
        'tools': get_available_tools(),
        'agent': True,
        'voice': False
    }

if __name__ == "__main__":
    # Initialize environment
    initialize_env()
    
    # Create or update configuration
    create_config()
