from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain_community.agent_toolkits.load_tools import load_tools
from helpers.agent_prompt import get_agent_prompt, get_agent_prompt_for_gemini
import uuid
from helpers.llm import get_chain
from helpers.llm import get_llm
from tools import * 

def create_agent(llm, memory, selected_tools):
    tools = []
    if "Search" in selected_tools:
        tools.extend(load_tools(["serpapi"], llm=llm))
    if "Gmail" in selected_tools:
        from tools.gmail_tools import send_mail, search_google, get_thread, create_draft, get_message, get_gmail_ids, get_date, create_event, get_events
        tools.extend([send_mail, search_google, get_thread, create_draft, get_message, get_gmail_ids, get_date, create_event, get_events])
    
    custom_tools = {
        "Finance": yfinance_tool,
        "Location": mylocation,
        "Weather": weather_tool,
        "File Operations": file_tools,
        "Shell": shell_tool,
        "Date and Time": [get_today_date, get_current_time],
        "Media": play_youtube,
        "System": [restart_laptop, shutdown_laptop, check_battery],
        "Volume Control": [increase_volume, decrease_volume, mute_volume, umute_volume],
        "Python": python_tool,
        "Knowledge": internal_knowledge_tool,
        "Bluetooth": [connect_bluetooth_device, disconnect_bluetooth_device, bluetooth_available_devices, turn_on_bluetooth, turn_off_bluetooth],
        "WhatsApp": send_whatsapp_message,
        "Alarm": set_alarm_or_timer, 
        "Screenshare": screenshare_tool,
        "Note Taking": note_taking_tool,
        "To-Do List": to_do_list_tool,
    }
    
    for tool, tool_func in custom_tools.items():
        if tool in selected_tools:
            if isinstance(tool_func, list):
                tools.extend(tool_func)
            else:
                tools.append(tool_func)
    
    prompt = get_agent_prompt_for_gemini() if isinstance(llm, ChatGoogleGenerativeAI) else get_agent_prompt()
    agent = create_structured_chat_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=10, handle_parsing_errors=True, memory=memory)

def update_llm_and_chain():
    import streamlit as st
    st.session_state.llm = get_llm(
        temperature=st.session_state.temperature,
        provider=st.session_state.llm_provider,
        model=st.session_state.model
    )
    st.session_state.chain = get_chain(llm=st.session_state.llm, memory=st.session_state.memory)
    if st.session_state.use_agent:
        st.session_state.agent = create_agent(st.session_state.llm, st.session_state.memory, st.session_state.selected_tools)
    else:
        st.session_state.agent = None

def initialize_session_state():
    import streamlit as st
    from langchain.memory import ConversationBufferWindowMemory
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationBufferWindowMemory(k=5, return_messages=True, memory_key='chat_history')
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'use_agent' not in st.session_state:
        st.session_state.use_agent = True
    if 'use_voice' not in st.session_state:
        st.session_state.use_voice = False
    if 'stop_signal' not in st.session_state:
        st.session_state.stop_signal = False
    if 'uuid' not in st.session_state:
        st.session_state.uuid = str(uuid.uuid4())
    if 'last_audio_bytes' not in st.session_state:
        st.session_state.last_audio_bytes = None
