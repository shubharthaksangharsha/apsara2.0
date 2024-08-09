#Required libs
import os 
import multiprocessing
import subprocess
from langchain.tools import tool
import psutil as ps 
import subprocess 




#function to get bluetooth devices list 
def bluetooth_list() -> list:
    '''
    useful when to find the available devices list of bluetooth devices
    use this tool to find the mac address of bluetooth device before connecting to bluetooth device
    returns: list
    '''
    output = subprocess.check_output("bluetoothctl devices", shell=True, universal_newlines=True)
    output = str(output).strip('\n')
    lines = output.split('\n')
    devices = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            mac_address = parts[1]
            device_name = ' '.join(parts[2:])
            devices.append({device_name: mac_address})
    return devices

#Bluetooth available devices tool
@tool
def bluetooth_available_devices() -> list:
    '''
    useful when to find the available devices list of bluetooth devices
    use this tool to find the mac address of bluetooth device before connecting to bluetooth device
    returns: list
    '''
    output = subprocess.check_output("bluetoothctl devices", shell=True, universal_newlines=True)
    output = str(output).strip('\n')
    lines = output.split('\n')
    devices = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            mac_address = parts[1]
            device_name = ' '.join(parts[2:])
            devices.append({device_name: mac_address})
    return devices

#Power off blueooth 
@tool 
def turn_off_bluetooth()-> str:
    '''
    useful when to turn off bluetooth
    returns: str
    '''
    power = subprocess.check_output(
        "bluetoothctl power off", shell = True, universal_newlines=True
    )
    print(power)
    return power

#Power on blueooth 
@tool
def turn_on_bluetooth()-> str:
    """
    useful when to turn on bluetooth
    returns: str
    """
    power = subprocess.check_output(
        "bluetoothctl power on", shell = True, universal_newlines=True
    )
    print(power)
    return power

#disconnect to bluetooth device
@tool 
def disconnect_bluetooth_device(disconnect='disconnect')-> str:
    '''
    useful when to disconnect to bluetooth device
    disconnect: str = disconnect
    returns: str
    '''
    disconnect = subprocess.check_output(
        "bluetoothctl disconnect", shell = True, universal_newlines=True
    )
    print(disconnect)
    return disconnect

# connect to bluetooth device
@tool
def connect_bluetooth_device() -> str:
    """
    useful when to connect to bluetooth device
    returns: str
    """
    name, mac = bluetooth_list()[0].popitem()
    print(name, mac)
    connected = subprocess.check_output(
        "bluetoothctl connect " + mac, shell = True, universal_newlines=True
    )
    print(connected)
    return 'Successfully connected to ' + name 

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

#Shutdown laptop tool
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
    

#Restart laptop tool
@tool 
def restart_laptop() -> str: 
    '''
    useful when you user ask to restart the laptop 
    '''
    try:
        os.system(f"reboot")
    except Exception as e:
        print(e)
        return "Something went wrong while rebooting down the laptop"
    return f"Laptop will reboot in 1 minute"

#Increase volume tool
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

#Decrease volume tool    
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

#Mute volume tool
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
    
#Unmute volume tool    
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

if __name__ == '__main__':
    pass