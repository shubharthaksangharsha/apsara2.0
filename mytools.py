from langchain.agents import Tool
import os 
from langchain_community.tools.file_management.read import ReadFileTool
from langchain_community.tools.file_management.write import WriteFileTool
from langchain_community.utilities.python import PythonREPL
from langchain_experimental.tools import PythonAstREPLTool, PythonREPLTool
from langchain_community.utilities.openweathermap import OpenWeatherMapAPIWrapper
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun #requires internet
import psutil as ps 
import datetime
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool #requires internet 




@tool
def internal_knowledge_tool(input: str = 'final answer', answer: str = 'unknown') -> str:
    '''
    Useful tool when already know the answer to the user query
    input: str = 'final answer' - default value. It just serves as a safety purpose so that it won't run into any errors.
    answer: str = 'unknown' - default value. The answer that you already knows.
    Use this tool when you already knows the answer to what user is asking and doesn't need to use any other tools.
    Return the final answer if you already knows the answer. Also, while returning it should treat the answer as final answer.
    '''
    return f'{answer}'
    


#Find Phone 
@tool  
def find_or_ring_phone(find: str = 'find'):
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
#requires internet
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
    