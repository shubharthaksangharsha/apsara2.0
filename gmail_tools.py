from langchain.tools import tool
import datetime 
from datetime import timedelta
import os 
import pytz
import re
import json 

#Gmail tool libs 
from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials)
from google.oauth2.credentials import Credentials
from langchain_community.tools.gmail.send_message import GmailSendMessage
from langchain_community.tools.gmail.create_draft import GmailCreateDraft
from langchain_community.tools.gmail.get_message import GmailGetMessage
from langchain_community.tools.gmail.search import GmailSearch
from langchain_community.tools.gmail.get_thread import GmailGetThread



#Get the gmail required credential 
def get_gmail_credential(service_name='gmail', service_version='v1'):
    #Read this to create your own credentials: https://developers.google.com/gmail/api/quickstart/python        
    credentials = get_gmail_credentials(
        token_file='token.json', 
        scopes=["https://mail.google.com/", "https://www.googleapis.com/auth/calendar"],
        client_secrets_file="credentials.json",
    )

    api_resource = build_resource_service(service_name=service_name, service_version= service_version, credentials=credentials)
    
    return api_resource

#Gmail tools  - Completed 
send_mail = GmailSendMessage(api_resource=get_gmail_credential())
create_draft = GmailCreateDraft(api_resource=get_gmail_credential())
get_message = GmailGetMessage(api_resource=get_gmail_credential())
search_google = GmailSearch(api_resource=get_gmail_credential())
get_thread = GmailGetThread(api_resource=get_gmail_credential())

#Get gmail ids 
@tool 
def get_gmail_ids(check: bool=True) -> dict: 
    '''
    #ALWAYS USE THIS TOOL FIRST TO BEFORE USING ANY GMAIL/CALENDAR TOOL.
    use this tool when you want to find gmail id of a user if not mentioned. 
    Use this tool as begining of ANY TOOL RELATED TO MAIL/ CALENDAR-RELATED FUNCTIONS. 
    It is recommended to use this function before utilizing any Google/Gmail/Calendar-related functions to ensure that the required Gmail IDs are available.
    useful to get gmail ids.
    check: bool = True. Uses just for safety purposes so that it won't run into errors 
    Returns: dict of gmail ids 
    '''
    with open('gmail_ids.json', 'r') as f:
        gmail_ids = json.load(f)
    
    return gmail_ids


#Set calendar meeting 
@tool
def get_date(text: str ) -> datetime.date:
    '''
    Useful to to get date for setting calendar meeting/events. 
    USE THIS TOOL FIRST WHEN CREATING MEETINGS/EVENTS
    text: str: query of the user from which date will be extracted. 
    Use this tool first to get the calendar meeting then use the output of the tool as an input parameter of `date` to create_event tool. 
    returns datetime.date 
    '''
    MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    DAY_EXTENTIONS= ["nd", "rd", "th", "st"]
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today
    if text.count("tomorrow") > 0:
        return today + timedelta(1)
    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    # THE NEW PART STARTS HERE
    if month < today.month and month != -1:  # if the month mentioned is before the current month set the year to the next
        year = year+1

    # This is slighlty different from the video but the correct version
    if month == -1 and day != -1:  # if we didn't find a month, but we have a day
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    # if we only found a dta of the week
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1:  
        return datetime.date(month=month, day=day, year=year)

#get upcoming events tool
@tool
def get_events(day:str="today") -> list[dict]:
    '''
    useful when to check upcoming google calendar events or meetings. 
    day: get date from user query. e.g: 'today', 'tomorrow'. Default is today
    '''
    service = get_gmail_credential(service_name='calendar', service_version='v3')
    day = get_date(day)
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    ist = pytz.timezone("Asia/Kolkata")
    date = date.astimezone(ist)
    end_date = end_date.astimezone(ist)
    event_result = service.events().list(calendarId = 'primary', timeMin=date.isoformat(),timeMax = end_date.isoformat(),singleEvents = True, orderBy='startTime').execute()# maxResults = n, 
    events = event_result.get('items', [])
    if not events:
        return 'No upcoming events found'
    else:
        print(f'You have {len(events)} events on this day.')        
        get_events = []
        for event in events:
            get_events.append(event)
        return get_events

#Create event/Meeting tool
@tool 
def create_event(day: datetime.date, mail: list = [], summary: str = '', meeting_time: str = '') -> str:
    """
    Useful when creating Google Calendar events or meetings.
    use gmail addresses of the people you want to invite from get_gmail_ids tool if the gmail id is not mentioned. 
    day: datetime.date: The date of the event. [Get the date from user query] 
    mail: List of emails to whom you want to invite.
    summary: Short description of the event.
    meeting_time: Time of the event to be held (format: "HH:MM AM/PM").
    """

    try:
        # Parsing the meeting time from the input string if not provided
        match = re.search(r'at (\d{1,2}:\d{2} [ap]m)', meeting_time)
        if match:
            meeting_time = datetime.strptime(match.group(1), '%I:%M %p').strftime('%H:%M')
        print(meeting_time)
        meeting_time = meeting_time.replace('AM', '').replace('PM', '').replace('am', '').replace('pm', '').strip()

        # Parsing time and setting start and end times
        start_time = datetime.datetime.combine(day, datetime.datetime.strptime(meeting_time, '%H:%M').time())
        end_time = start_time + timedelta(minutes=59)

        # Setting timezone
        timezone = 'Asia/Kolkata'

        # Creating event object
        event = {
            'summary': summary,
            'location': 'Delhi',
            'description': summary,
            'start': {
                'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': timezone,
            },
            'attendees': [{'email': mail}],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        # Inserting event into calendar
        service = get_gmail_credential(service_name='calendar', service_version='v3')
        event = service.events().insert(calendarId='shubharthaksangharsha@gmail.com', sendUpdates='all',
                                          body=event).execute()
        return f'Event has been created: {event.get("htmlLink")}'

    except Exception as e:
        return f'Unable to create the event: {e}'
