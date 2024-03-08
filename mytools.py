from langchain.agents import Tool, load_tools
import os 
from langchain_community.tools.file_management.read import ReadFileTool
from langchain_community.tools.file_management.write import WriteFileTool
from langchain_community.utilities.python import PythonREPL
from langchain_community.utilities.serpapi import SerpAPIWrapper
from langchain_community.utilities.openweathermap import OpenWeatherMapAPIWrapper
from langchain.tools import BaseTool, StructuredTool, tool
from find_phone import * 
from pepper import * 
import psutil as ps 
import webbrowser
import datetime
import pywhatkit




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
    
#Find Phone 
@tool 
def find_phone():
    '''
    useful to find user android device name - One Plus Node. 
    returns True if no errors occured during findmyphone() else return False means some error occurred  

    '''
    find = findmyphone()
    print(find)
    if find == True: 
        return "Ringed the phone"
    else: 
        return "Some error occurred please try again later."



@tool
def play_youtube(song_name: str):
    '''
    useful to play songs on youtube. 
    song_name:str - Song name of user wants to play 
    Play song_name for user. Use when user wants to play any song on Youtube. 
    '''
    # pywhatkit.playonyt(song_name)
    return f"Playing {song_name} on Youtube"

#Current Location for Weather 
@tool 
def mylocation():
    '''
    Useful when want to get users current location.
    it is used for openweather api if user ask for current location for weather input.
    '''
    return "Kharar, Punjab, India"

#Get Today Date 
@tool
def get_today_date():
    '''
    Useful when you want to find today's date 
    '''
    date = datetime.datetime.today()
    return date.strftime("Date: %Y-%m-%d")

#Weather Tool 
weather_tool = Tool(
    name='openweather',
    func=OpenWeatherMapAPIWrapper().run,
    description='useful to get weather details of any location'
)

# Python Repl Tool
python_tool = Tool(
    name='python-repl', 
    func=PythonREPL().run,
    description='useful to execute python code.')

read_tool = ReadFileTool()
write_tool = WriteFileTool()

if __name__ == '__main__':
    print(get_today_date.name)
    print(get_today_date.description)
    print(get_today_date.args)
    