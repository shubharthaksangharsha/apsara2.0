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
def check_battery(battery_string: str = "battery") -> str:
    '''
    useful when you need to find the current battery percentage and whether laptop battery is charging or not.
    battery_string: str = "battery", default value is "battery". it just for safety purpose so that it won't run into any errors.
    the tool will return the battery percentage and whether laptop is charging or not.
    returns: str
    '''
    try:
        percent = int(ps.sensors_battery().percent)
        charging = ps.sensors_battery().power_plugged
        if charging:
            return f"Laptop is {percent}% charged and currently charging"
        else:
            return f"Laptop is {percent}% charged and currently not charging"
    except Exception as e:
        print(e)
        return "Something went wrong while checking the battery"
    
    return check_battery(input_args={})

@tool
def shutdown_laptop() -> str: 
    '''
    useful when you user ask to power off or shutdown the laptop 
    '''
    try:
        os.system(f"shutdown")
        return f"Laptop will shutdown in 1 minute"
    except Exception as e:
        print(e)
        return "Something went wrong while shutting down the laptop"
    


@tool 
def restart_laptop() -> str: 
    '''
    useful when you user ask to restart the laptop 
    '''
    try:
        os.system(f"reboot")
        return f"Laptop will shutdown in 1 minute"
    except Exception as e:
        print(e)
        return "Something went wrong while shutting down the laptop"

@tool
def increase_volume(volume_change: int = 10000) -> str:
    '''
    useful when you user ask to increase the volume of laptop 
    volume_change: int = 10000, default value is 10000
    volume_change = 1000 means 1% of volume will be increased
    volume_change = 2000 means 2% of volume will be increased
    if you want to increase the volume by 5% then volume_change = 5000
    returns: str
    #Return the final answer if found successfully in output
    '''
    try:
        os.system(f'pactl set-sink-volume @DEFAULT_SINK@ +{volume_change}')
        return f"Successfully increased volume by {volume_change}"
    except Exception as e:
        print(e)
        return "Something went wrong while increasing the volume"
@tool
def decrease_volume(volume_change: int = 10000) -> str:
    '''
    useful when you user ask to decrease the volume of laptop 
    volume_change: int = 10000, default value is 10000 
    volume_change = 1000 means 1% of volume will be decreased
    returns: str
    Return the final answer if found successfully in output
    '''
    try:
        os.system(f'pactl set-sink-volume @DEFAULT_SINK@ -{volume_change}')
        return f"Successfully decreased volume by {volume_change}"
    except Exception as e:
        print(e)
        return "Something went wrong while decreasing the volume"

@tool  
def mute_volume(muting_volume: str = "mute") -> str:
    '''
    useful when you user ask to mute the volume of laptop 
    muting_volume: str = mute. default value is "mute". it just for safety purpose so that it won't run into any errors.
    returns: str
    Return the final answer if found successfully in output
    '''
    try:
        os.system(f'pactl set-sink-mute @DEFAULT_SINK@ toggle')
        return f"Successfully muted the volume."
    except Exception as e:
        print(e)
        return "Something went wrong while muting the volume"
@tool  
def umute_volume(unmuting_volume: str = "unmute") -> str:
    '''
    useful when you user ask to unmute the volume of laptop 
    unmuting_volume: str = unmute. default value is "unmute". it just for safety purpose so that it won't run into any errors.
    returns: str
    Return the final answer if found successfully in output
    '''
    try:
        os.system(f'pactl set-sink-mute @DEFAULT_SINK@ toggle')
        return f"Successfully unmuted the volume."
    except Exception as e:
        print(e)
        return "Something went wrong while unmuting the volume"
