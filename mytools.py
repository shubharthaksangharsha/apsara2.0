from langchain.agents import Tool
import os 
from typing import List, Optional
from tempfile import TemporaryDirectory
from langchain_community.agent_toolkits import FileManagementToolkit
working_directory = TemporaryDirectory()


from langchain_community.tools.file_management.read import ReadFileTool
from langchain_community.tools.file_management.write import WriteFileTool
# from langchain_community.utilities.python import PythonREPL
from langchain_experimental.utilities.python import PythonREPL
from langchain_experimental.tools import  PythonREPLTool
from langchain_community.utilities.openweathermap import OpenWeatherMapAPIWrapper
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun #requires internet
import psutil as ps 
import datetime
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool #requires internet 
import requests
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import subprocess
from langchain_community.tools.shell import ShellTool
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_sync_playwright_browser
#from langchain_community.tools.google_cloud import GoogleCloudTextToSpeechTool #TODO

#Load environment variables 
load_dotenv()

#File management tool 
toolkit = FileManagementToolkit() 
file_tools = toolkit.get_tools()

#Shell tool 
shell_tool = ShellTool()

#Playwright tool 
sync_browser = create_sync_playwright_browser()
toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
playwright_tools = toolkit.get_tools()

#Get all apps installed
@tool
def get_installed_applications(check: bool =True) -> Optional[List[str]]:
    '''
    useful when you want to finds all the apps installed on your system.
    #Use this tool when you want to find all the apps installed on your system.
    use as a pre-requisite for launch_app_tool.
    check: bool = True: It just serves as a safety purpose so that it won't run into any errors.
    return: list - a list of all files in the /bin/ directory. 
    Look for app name  from the output of get_installed_applications tool and use launch_app_tool to launch the app.
    '''
    try:
        # Get a list of all files in the /bin/ directory
        bin_files = []
        # bin_files = os.listdir('/bin/')
        bin_files.extend(os.listdir('/snap/bin/'))
        return bin_files
    except FileNotFoundError:
        print("Error: /bin/ directory not found.")
        return []
    except Exception as e:
        print("Error occurred:", e)
        return e

@tool
def launch_app_tool(app_name: str) -> str:
    '''
    useful when you want to launch or open an app on your system.
    app_name: str - name of the app you want to launch.
    use get_installed_applications tool to get the app_name.
    return: str - the output of the command.
    '''
    try:
        # Check if the app is installed
        output = subprocess.Popen([app_name])
        print(output)
        return f'Successfully launched {app_name}'
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e)
        return e
    except Exception as e:
        print("Error occurred:", e)
        return e 

#Get my location tool 
@tool
def mylocation(location: str=True) -> str:
    '''
    useful when you want to find your current location.
    location:str = True. Use this parameter only for safe execution of the tool.
    return current location name.
    '''
    try:
        # Fetching current location using ipinfo.io
        response = requests.get('https://ipinfo.io')
        data = response.json()
        location = data.get('loc')
        if location:
            latitude, longitude = location.split(',')
        else:
            print("Location not found.")
            return 'Location not found'

        # Reverse geocoding to get location name
        geoLoc = Nominatim(user_agent="GetLoc")
        location_name = geoLoc.reverse(f"{latitude}, {longitude}")
        return location_name.address

    except Exception as e:
        print("Error occurred:", e)
        return f'Error occurred:, {e}'

#Internal Knowledge tool 
@tool
def internal_knowledge_tool(input: str = 'final answer', answer: str = 'This is the answer') -> str:
    '''
    A tool to return a predefined answer when the response is already known.

    Parameters:
    input (str): A default parameter to ensure the function has an input. It can be used to pass context if needed.
    answer (str): The answer to return when the tool is called. Defaults to a general placeholder answer.

    Returns:
    str: The predefined answer provided as input to the function.
    '''
    return answer

    


#Find Phone 
@tool  
def find_or_ring_phone(find: str = 'find') -> str:
    #requires internet
    #TODO
    '''
    useful to find or ring user android device name - One Plus Node. 
    find: str = 'find' - default value. it just for safety purpose so that it won't run into any errors 
    '''
    try:
        os.system('python find_phone.py')
        return "Ringed the phone"
    except Exception as e:
        return "Error: " + str(e)
    

#Get Today Date 
@tool 
def get_today_date(check_date: bool =True) -> str:
    '''
    Useful when you want to find today's date in the format of YYYY-MM-DD.
    check_date -> bool = True: for safety purpose so that it won't run into any errors.
    return: str - today's date in the format of YYYY-MM-DD.
    Useful to get date for openweather api and other tools such as creating an meeting or event.
    '''
    date = datetime.datetime.today()
    return date.strftime("Date: %Y-%m-%d")

@tool
def get_current_time(check_time: bool = True):
    """
    Function to get the current time.
    check_time -> bool = True: 
    return: str - Current time in the format 'HH:MM:SS'.
    Returns:
        str: Current time in the format 'HH:MM:SS'.
    """
    return datetime.datetime.now().strftime('%H:%M:%S')

#Weather Tool 
#requires internet
weather_tool = Tool(
    name='openweather',
    func=OpenWeatherMapAPIWrapper().run,
    description='useful to get weather details of any location'
)

# Python Repl Tool
python_tool = PythonREPLTool()

#Playwright Tool 

#search tool 
#requires internet
search_tool = Tool(
    name='duckduckgo',
    func=DuckDuckGoSearchRun().run,
    description='useful to search anything on the internet.'
)

#read tool 
read_tool = ReadFileTool()

#yfinance_tool 
yfinance_tool = Tool(
    name='Yahoo Finance', 
    description='''
    useful when you want to find stock price or useful financial news about an public company. Input should takes an company ticker , use your knowledge to get the ticker value of any company. 
    for example: Google has ticker value as GOOG, similarly, NVIDIA has NVDA. 
    ''',
    func= YahooFinanceNewsTool().run
    
)

#write tool
@tool
def write_save_tool(file_path: str, content: str) -> str:
    '''
    useful when you want to write/save the content in a file.
    file_path: str - path of the file in which you want to write.
    content: str - content you want to write in the file_path.
    return: str - the content of the file
    '''
    try:
        with open(file_path, 'a') as f:
            f.write(content)   
        return f'{content} written to {file_path}'
    except Exception as e:
        return "Error: " + str(e)

if __name__ == '__main__':
    pass 
    

    
