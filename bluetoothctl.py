import time
import pexpect
import subprocess
import sys

def init():
    subprocess.check_output("rfkill unblock bluetooth", shell = True)


def get_mac_address():
    output = available_devices()
    if len(output) == 0:
        return None
    for device in output:
        for key, value in device.items():
            return key, value

def available_devices():
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


def turn_off_bluetooth():
    power = subprocess.check_output(
        "bluetoothctl power off", shell = True, universal_newlines=True
    )
    print(power)
    return power

def turn_on_bluetooth():
    power = subprocess.check_output(
        "bluetoothctl power on", shell = True, universal_newlines=True
    )
    print(power)
    return power

# connect to device
def connect(mac):
    connected = subprocess.check_output(
        "bluetoothctl connect " + mac, shell = True, universal_newlines=True
    )
    print(connected)
    return connected

if __name__ == '__main__':
    init()
    _, mac = get_mac_address()
    # turn_on_bluetooth()
    # time.sleep(1)
    connect(mac)
    # turn_off_bluetooth()
    # time.sleep(1)
    # turn_on_bluetooth()
    # time.sleep(1)
    # connect(mac)

