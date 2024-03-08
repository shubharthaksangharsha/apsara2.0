import os 
from langchain.tools import tool
from find_phone import * 
from spotify_utils import * 
import psutil as ps 
import pandas as pd 
import spotipy as sp 
from spotipy import SpotifyOAuth
import pywhatkit
import time 




def spotify_helper():
    # variables from setup.txt
        print('shubhi')
        setup = pd.read_csv('./setup.txt', sep='=', names = ['key', 'value'])
        setup = dict(zip(setup['key'], setup['value']))
        client_id = setup['client_id']
        client_secret = setup['client_secret']
        device_name = "shubharthak-Inspiron-16-Plus-7620"
        device_name3 = 'Web Player (Chrome)'
        device_name2 = 'EB2101'
        redirect_uri = setup['redirect_uri']
        scope = setup['scope']
        username = setup['username']
        # Connecting to the Spotify account
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            username=username)
        print(f'Auth manager = {auth_manager}')
        spotify = sp.Spotify(auth_manager=auth_manager)
        
        try:
            # Selecting device to play from
            devices = spotify.devices()
            print(devices)
            deviceID = {}
            
            for d in devices['devices']:
                d['name'] = d['name'].replace('’', '\'')
                if d['name'] == device_name:
                    deviceID[d['name']] = d['id']
                    continue
                if d['name'] == device_name2:
                    deviceID[d['name']] = d['id']
                    continue
                if d['name'] == device_name3:
                    deviceID[d['name']] = d['id']
                    continue
        except Exception as e:
            print(e)
            print('error occured')

        return spotify,deviceID

#Play on Youtube
@tool
def play_youtube(song_name: str):
    '''
    useful to play songs on youtube. if spotify is not available then youtube is used. 
    song_name:str - Song name of user wants to play 
    Play song_name for user. Use when user wants to play any song on Youtube. 
    '''
    pywhatkit.playonyt(song_name)
    return f"Playing {song_name} on Youtube"

##Get Spotify Song playing 
def print_current_song_func() -> str:
    '''
    useful when you need to find out the current song playing on spotify. 
    if nothing is playing return "No song is currently playing right now."
    '''
    spotify, device_name = spotify_helper()
    data = spotify.current_playback()
    try: 
        if 'item' in data and 'name' in data['item'] and 'artists' in data['item'] and len(data['item']['artists']) > 0:
            print('inside the loop')
            song_name = data['item']['name']
            print('got the song name')
            artist_name = data['item']['artists'][0]['name']  # Assuming only one artist
            print('got the artist name')
            device_name = data['device']['name']
            print("Current Song:", song_name)
            print("Artist:", artist_name)
            print("Device:", device_name)
            return f"Current Song Playing: {song_name} by {artist_name} on {device_name}"
        else:
            return "No song is currently playing right now."
    except Exception as e :
        print(e) 
        return "No song is currently playing right now."
    
#Get Spotify Song playing 
@tool
def print_current_song_details() -> str:
    '''
    useful when you need to find out the current song playing on spotify. 
    if nothing is playing return "No song is currently playing right now."
    '''
    spotify, device_name = spotify_helper()
    data = spotify.current_playback()
    try: 
        if 'item' in data and 'name' in data['item'] and 'artists' in data['item'] and len(data['item']['artists']) > 0:
            print('inside the loop')
            song_name = data['item']['name']
            print('got the song name')
            artist_name = data['item']['artists'][0]['name']  # Assuming only one artist
            print('got the artist name')
            device_name = data['device']['name']
            print("Current Song:", song_name)
            print("Artist:", artist_name)
            print("Device:", device_name)
            return f"Current Song Playing: {song_name} by {artist_name} on {device_name}"
        else:
            return "No song is currently playing right now."
    except Exception as e :
        print(e) 
        return "No song is currently playing right now."


#Detect Spotify Device 
@tool
def detect_spotify_device(query: str= 'laptop') -> str:
    '''
    useful when need to get the device ID to play spotify song. 
    use this tool as a way to get the deviceName from the query 
    if Nothing is specified as laptop, phone or browser use laptop as default. 
    '''
    try:        
        _, devices = spotify_helper()
        if len(devices.keys()) == 0:
            return 'Spotify is not opened yet'
        # for key in devices.keys():
        #     print(key)
        #     if key == 'Web Player (Chrome)':
        #         return 'Web Player (Chrome)'
        #     if key == 'EB2101':
        #         return 'EB2101'
        #     if key == 'shubharthak-Inspiron-16-Plus-7620':
        #         return 'shubharthak-Inspiron-16-Plus-7620'
    except Exception as e :
        print(e)
        return "Exception occurred unable to play"
    
    try:

        if query is None:
            return 'shubharthak-Inspiron-16-Plus-7620'
        if 'laptop' in query:
            return 'shubharthak-Inspiron-16-Plus-7620'
        if 'phone' in query:
            return 'EB2101'
        if 'browser' in query or 'web' in query:
            return 'Web Player (Chrome)'
        return 'shubharthak-Inspiron-16-Plus-7620'
    except Exception as e :
        print(e)
        return "Exception occurred unable to play"


        
    

#Play song on Spotify 
@tool
def play_spotify(song_name: str, device_name: str="shubharthak-Inspiron-16-Plus-7620") -> str:
    '''
    useful when you need to play a song on spotify. 
    Detect the song_name from query
    device_name = "shubharthak-Inspiron-16-Plus-7620" for laptop
    device_name3 = 'Web Player (Chrome)' for browser
    device_name2 = 'EB2101' for phone
    You should able to detect the deviceID from the detect_spotify_tool tool if nothing provided use shubharthak-Inspiron-16-Plus-7620 as default.
    Remember: Always use detect_spotify_tool first before playing song on spotify. 
    for e.g: 
        play feel it by michelle morone on laptop 
        song_name: 'feel it - michelle morone'
        deviceID: 'shubharthak-Inspiron-16-Plus-7620'

        play feel it by michelle morone on phone 
        song: 'feel it - michelle morone'
        deviceID: 'EB2101'
    if not song is defined play any random song you know on spotify. 
    '''
    spotify, deviceID = spotify_helper()
    try: 
        print('Song name:', song_name)
        uri = get_track_uri(spotify=spotify, name=song_name)
        print(f"Track: {uri}")
        play_track(spotify=spotify, device_id=deviceID[device_name], uri=uri)
        time.sleep(0.5)
        return print_current_song_func()
    except Exception as e :
        print(e) 
        return "Error playing song"
    

    
#Open Spotify App 
@tool
def open_spotify(query: str='app') -> str: 
    '''
    useful when you need to open spotify on user laptop.
    query can be spotify app, or browser. default is spotify app
    '''
    try: 
        if 'app' in query:
            os.system('spotify &')
            time.sleep(1)
            return "Opening Spotify on laptop"
        if 'browser' in query:
            time.sleep(3)
            os.system('chromium https://open.spotify.com/ &')
            return "Opening Spotify"
        os.system('spotify &')
        return "Opening Spotify"
    except: 
        return "Error opening Spotify"

# #Set Spotify 
# @tool
# def set_spotify()