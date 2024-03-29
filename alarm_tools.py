import subprocess
import random 
from langchain.tools import tool   

@tool
def set_alarm_or_timer(alarm_time=None, message="Alarm!", sound_file=random.choice(['alarm.mp3', 'alarm2.mp3', 'alarm3.mp3']), timer_duration="5s", alarm_date=None):
    """
    Sets an alarm or a timer with specified options.

    Args:
        alarm_time (str): Time for the alarm in format HH:MM (24-hour format).
        message (str): Message to display when the alarm goes off (default: "Alarm!").
        sound_file (str): Path to the sound file to play when the alarm goes off (default: random choice between "alarm.mp3", "alarm2.mp3", "alarm3.mp3").
        timer_duration (str): Duration for the timer (format: '5s' for 5 seconds, '1h5m2s' for 1 hour 5 minutes 2 seconds) (default: "5s").
        alarm_date (str): Date for the alarm in format YYYY-MM-DD (default: today's date).

    Note:
        - If `alarm_time` is provided, it will set an alarm for that specific time.
        - If `timer_duration` is provided, it will set a timer for the specified duration.
        - If both `alarm_time` and `timer_duration` are provided, it will prioritize setting the alarm.

    Example:
        # Set an alarm for 10:30 AM with a custom message and sound file
        set_alarm_or_timer(alarm_time="10:30", message="Wake up!", sound_file="alarm.mp3")

        # Set a timer for 15 minutes with the default message and sound file
        set_alarm_or_timer(timer_duration="15m")

        # Set an alarm for 9:00 PM on a specific date with a custom message
        set_alarm_or_timer(alarm_time="21:00", message="Reminder for the event!", alarm_date="2024-04-01")

        # Set a timer for 1 hour and 30 minutes with a custom sound file
        set_alarm_or_timer(timer_duration="1h30m", sound_file="custom_sound.wav")

        # Set an alarm for 7:00 AM with the default message and sound file
        set_alarm_or_timer(alarm_time="07:00")
    """

    # Default values
    default_date = subprocess.check_output(["date", "+%Y-%m-%d"]).decode().strip()
    default_timer_duration = "5s"
    default_sound_file = random.choice(['alarm.mp3', 'alarm2.mp3', 'alarm3.mp3'])

    # Set default date if not provided
    if alarm_date is None:
        alarm_date = default_date

    # Check if either time or timer is provided
    if not alarm_time and not timer_duration:
        print("Error: Please specify either a time for the alarm or a timer duration.")
        return

    # Check if sound file or message is provided
    if not message and alarm_time:
        print("Error: Please provide either a sound file or a message for the alarm.")
        return

    # Construct command
    shell_script_path = "./alarm.sh"
    command = [shell_script_path]
    if alarm_time:
        command.extend(["-t", alarm_time])
    if message:
        command.extend(["-m", message])
    if sound_file:
        command.extend(["-s", sound_file])
    if timer_duration:
        command.extend(["-T", timer_duration])
    if alarm_date:
        command.extend(["-d", alarm_date])

    # Run command in background
    print('Command:', command)
    command.extend([' &'])
    subprocess.Popen(command)
    return "Done. Successfully set alarm/timer."

if __name__ == '__main__':
    # alarm(timer_duration="2s", message="Wake up!", sound_file="/path/to/soundfile.mp3")
    pass
    
