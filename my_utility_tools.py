from langchain.agents import Tool
import os 
from langchain_community.utilities.python import PythonREPL
from langchain_community.utilities.serpapi import SerpAPIWrapper
from langchain_community.utilities.openweathermap import OpenWeatherMapAPIWrapper
from langchain.tools import tool
from find_phone import * 
from spotify_utils import * 
import psutil as ps 

#check battery of laptop 
@tool
def check_battery() -> str:
    '''
    useful when you need to find the current battery percentage and whether laptop battery is charging or not.
    '''
    percent = int(ps.sensors_battery().percent)
    charging = ps.sensors_battery().power_plugged
    if charging:
        return f"Laptop is {percent}% charged and currently charging"
    else:
        return f"Laptop is {percent}% charged and currently not charging"
    

@tool
def shutdown_laptop(second: str = 60) -> str: 
    '''
    useful when you user ask to power off or shutdown the laptop 
    '''
    second = int(second)
    try:
        os.system(f"shutdown /s /t {second}")
    except Exception as e:
        print(e)
    return f"Laptop will shutdown in {second} seconds"

@tool 
def cancel_shutdown_laptop() -> str: 
    '''
    useful when you user ask to cancel shutdown the laptop 
    '''
    os.system("shutdown /a")
    return "Shutdown cancelled"

@tool 
def restart_laptop(second: str = 5) -> str: 
    '''
    useful when you user ask to restart the laptop 
    '''
    second = int(second)
    try:
        command = "shutdown /r /t 5"
        os.system(command=command)
    except Exception as e:
        print(e)
    return f"Laptop will restart in {second} seconds"

@tool 
def cancel_restart_laptop() -> str: 
    '''
    useful when you user ask to cancel restart the laptop 
    '''
    os.system("shutdown /a")
    return "Restart cancelled"