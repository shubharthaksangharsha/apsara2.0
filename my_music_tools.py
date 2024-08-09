import os 
from langchain.tools import tool

from spotify_utils import * 
import psutil as ps 
import pandas as pd 
import spotipy as sp 
from spotipy import SpotifyOAuth
import pywhatkit #require net and GUI too 
import time 



#Spotify_helper to get spotify object and devices dict 
def spotify_helper():
    # variables from setup.txt
        print('shubhi')
        setup = pd.read_csv('./.spotify_imp.txt', sep='=', names = ['key', 'value'])
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


#Play an album 
@tool 
def play_album_on_spotify(album_name: str, device_name: str) -> str:
    '''
    useful when user wants to play an album.
    album_name: str - Name of the album user wants to play. 
    device_name: str - Name of the device on which you want to play the album. 
    out: str - "Playing album_name on device_name" or "Device not found. Spotify is not opened on any device." or "Album not found."
    '''
    spotify, devices = spotify_helper()
    device_id = None
    for name, id in devices.items():
        if name == device_name:
            device_id = id
            break
    if device_id is None:
        return "Device not found. Spotify is not opened on any device."
    try:
        album_uri = get_album_uri(spotify=spotify, name=album_name)
        play_album(spotify=spotify, uri=album_uri, device_id=device_id)
        return f"Playing {album_name} on {device_name}"
    except Exception as e:
        print(e)
        return "Album not found."
    
#Play an artist  
@tool 
def play_artist_on_spotify(artist_name: str, device_name: str)-> str:
    '''
    useful when user wants to play an album.
    album_name: str - Name of the album user wants to play. 
    device_name: str - Name of the device on which you want to play the album. 
    out: str - "Playing artist_name on device_name" or "Device not found. Spotify is not opened on any device." or "artist not found."
   '''
    spotify, devices = spotify_helper()
    device_id = None
    for name, id in devices.items():
        if name == device_name:
            device_id = id
            break
    if device_id is None:
        return "Device not found. Spotify is not opened on any device."
    try:
        album_uri = get_artist_uri(spotify=spotify, name=artist_name)
        play_artist(spotify=spotify, uri=album_uri, device_id=device_id)
        return f"Playing {artist_name} on {device_name}"
    except Exception as e:
        print(e)
        return "Artist not found."


#Pause on Spotify
@tool 
def pause_or_resume_spotify(device_name: str, pause_or_play: str) -> str:
    '''
    useful when need to pause or resume the song on spotify. 
    device_name: str - Name of the device on which you want to pause or resume the song. 
    pause_or_play: str - 'pause' or 'play again' or 'resume'
    # Before using this tool get the device_name from the tool print_current_song_details to check which device is playing the song.
    # Then get the current device_name as a input. If no device is playing any song then return "No song is currently playing right now."
    use this tool as a way to pause or resume the song on spotify. 
    based on pause_or_play parameter it will pause or resume the song. 
    if user said to play again or resume then it will play resume the song. 
    if user said to pause then it will pause the song.     
    '''
    device_id = None
    spotify, devices = spotify_helper()
    if len(devices) == 0:
        return "Spotify is not opened on any device so can't pause the song"
    print(devices.keys())
    print(devices.values())
    print(devices.items())
    for name, id in devices.items():
        print(name, id)
        if name == device_name:
            device_id = id
            break
    if pause_or_play == 'pause':
            print('pausing the music')
            spotify.pause_playback(device_id=device_id)
            return f"Paused the song on {device_name}"
    if pause_or_play == 'resume' or pause_or_play == 'play again':
                print('resuming the music')
                spotify.start_playback(device_id=device_id)
                return f"Resumed the song on {device_name}"
    else:
        return "No song is currently playing right now."



#Play on Youtube
@tool
def play_youtube(song_name: str):
    #require net 
    '''
    useful to play songs on youtube. if spotify is not available then youtube is used. 
    song_name:str - Song name of user wants to play 
    Play song_name for user. Use when user wants to play any song on Youtube. 
    '''
    pywhatkit.playonyt(song_name)
    return f"Played {song_name} on Youtube"

##Get Spotify Song playing 
def print_current_song_func() -> str:
    '''
    useful when you need to find out the current song playing on spotify. 
    if nothing is playing return "No song is currently playing right now."
    shubharthak-Inspiron-16-Plus-7620 refers to laptop not phone 
    EB2101 refers to phone 
    Web Player (Chrome) refers to chrome browser     
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
def print_current_song_details(song_details: str ='song') -> str:
    '''
    useful when you need to find out the current song playing on spotify. 
    song_details: str: only for safety. 
    if nothing is playing return "No song is currently playing right now."
    '''
    spotify, device_name = spotify_helper()
    data = spotify.current_playback()
    print(data)
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
    remember for laptop use shubharthak-Inspiron-16-Plus-7620 
    remember for phone/android use EB2101 
    remember for browser use Web Player (Chrome) 
    '''
    try:        
        _, devices = spotify_helper()
        if len(devices.keys()) == 0:
            return 'Spotify is not opened yet'
        else:   
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
    Try to play song on spotify for 3 imes if not able to play then play it on youtube. 
    If song not available then play it on youtube using play_youtube tool 
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
    Also, if spotify is not opened yet, use `open_spotify` tool to open spotify. 
    '''
    spotify, deviceID = spotify_helper()
    try: 
        if len(deviceID.keys()) == 0:
            return 'Spotify is not opened yet'
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
    query can be spotify app, or browser. default is app
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

if __name__ == "__main__":
    pass
