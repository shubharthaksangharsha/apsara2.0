from langchain.agents import Tool
import os 
from langchain.tools import tool
from find_phone import * 
from pepper import * 
import psutil as ps 
import pandas as pd 
import spotipy as sp 
from spotipy import SpotifyOAuth


#Get Spotify Song playing 
@tool
def print_current_song_details():
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
            return song_name, artist_name, device_name
        else:
            return "No song is currently playing right now."
    except Exception as e :
        print(e) 
        return "No song is currently playing right now."


#Detect Spotify Device 
@tool
def detect_spotify_device(query: str) -> str:
    '''
    useful when need to get the device ID to play spotify song. 
    use this tool as a way to get the deviceName from the query 
    if Nothing is specified as laptop, phone or browser use laptop as default. 
    '''
    if 'laptop' in query:
        return 'shubharthak-Inspiron-16-Plus-7620'
    if 'phone' in query:
        return 'EB2101'
    if 'browser' in query:
        return 'Web Player (Firefox)'
    return 'shubharthak-Inspiron-16-Plus-7620'


def spotify_helper():
    # variables from setup.txt
        print('shubhi')
        setup = pd.read_csv('./setup.txt', sep='=', names = ['key', 'value'])
        setup = dict(zip(setup['key'], setup['value']))
        client_id = setup['client_id']
        client_secret = setup['client_secret']
        device_name = "shubharthak-Inspiron-16-Plus-7620"
        device_name3 = 'Web Player (Firefox)'
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
        except:
            print('error occured')
        return spotify,deviceID
    
#Play song on Spotify 
@tool
def play_spotify(song_name: str, device_name: str="shubharthak-Inspiron-16-Plus-7620") -> str:
    '''
    useful when you need to play a song on spotify. 
    Detect the song_name from query
    device_name = "shubharthak-Inspiron-16-Plus-7620" for laptop
    device_name3 = 'Web Player (Firefox)' for browser
    device_name2 = 'EB2101' for phone
    You should able to detect the deviceID from the detect_spotify_tool tool if nothing provided use shubharthak-Inspiron-16-Plus-7620 as default.
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
        return f"Playing {song_name} on {device_name}"
    except: 
        return "Error playing song"
    

    
#Open Spotify App 
@tool
def open_spotify(query: str) -> str: 
    '''
    useful when you need to open spotify on user laptop.
    '''
    try: 
        os.system('spotify &')
        return "Opening Spotify"
    except: 
        return "Error opening Spotify"
    