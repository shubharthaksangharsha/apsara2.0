#!/bin/bash

# Default alarm message, sound file, timer duration, and date
default_message="Alarm!"
default_sound_file="alarm3.mp3"
default_timer_duration="5s"
default_date=$(date '+%Y-%m-%d')

# Function to display usage information
usage() {
    echo "Usage: $0 [-t <time>] [-m <message>] [-s <sound_file>] [-T <timer>] [-d <date>]"
    echo "Options:"
    echo "  -t <time>       Specify the time for the alarm in format HH:MM (24-hour format)"
    echo "  -m <message>    Message to display when the alarm goes off (default: \"$default_message\")"
    echo "  -s <sound_file> Path to the sound file to play when the alarm goes off (default: \"$default_sound_file\")"
    echo "  -T <timer>      Set a timer for a duration (format: '5s' for 5 seconds, '1h5m2s' for 1 hour 5 minutes 2 seconds) (default: $default_timer_duration)"
    echo "  -d <date>       Specify the date for the alarm in format YYYY-MM-DD (default: today's date)"
    exit 1
}

# Parse command line options
while getopts "t:m:s:T:d:" opt; do
    case $opt in
        t) alarm_time=$OPTARG ;;
        m) message=$OPTARG ;;
        s) sound_file=$OPTARG ;;
        T) timer_duration=$OPTARG ;;
        d) alarm_date=$OPTARG ;;
        *) usage ;;
    esac
done

# Set default message if not provided
if [ -z "$message" ]; then
    message="$default_message"
fi

# Set default sound file if not provided
if [ -z "$sound_file" ]; then
    sound_file="$default_sound_file"
fi

# Set default timer duration if not provided
if [ -z "$timer_duration" ]; then
    timer_duration="$default_timer_duration"
fi

# Set default date if not provided
if [ -z "$alarm_date" ]; then
    alarm_date="$default_date"
fi

# Check if either time or timer is provided
if [ -z "$alarm_time" ] && [ -z "$timer_duration" ]; then
    echo "Error: Please specify either a time for the alarm or a timer duration."
    usage
fi

# Check if sound file or message is provided
if [ -z "$message" ] && [ -n "$alarm_time" ]; then
    echo "Error: Please provide either a sound file or a message for the alarm."
    usage
fi

# Calculate seconds until alarm
if [ -n "$alarm_time" ]; then
    current_time=$(date '+%s')
    alarm_seconds=$(date -d "$alarm_date $alarm_time" '+%s')
    # If alarm time is in the past, add one day to the alarm
    if [ $alarm_seconds -lt $current_time ]; then
        alarm_seconds=$((alarm_seconds + 86400))  # 86400 seconds in a day
    fi
    seconds_until_alarm=$((alarm_seconds - current_time))
fi

# Convert timer duration to seconds
if [ -n "$timer_duration" ]; then
    timer_seconds=0
    if [[ $timer_duration == *s ]]; then
        timer_seconds=$((timer_seconds + ${timer_duration%s}))
    fi
    if [[ $timer_duration == *m ]]; then
        timer_seconds=$((timer_seconds + ${timer_duration%m} * 60))
    fi
    if [[ $timer_duration == *h ]]; then
        timer_seconds=$((timer_seconds + ${timer_duration%h} * 3600))
    fi
fi

# Sleep until alarm time or timer duration
if [ -n "$alarm_time" ]; then
    if [ $seconds_until_alarm -gt 0 ]; then
        sleep $seconds_until_alarm
    fi
fi
if [ -n "$timer_duration" ]; then
    sleep $timer_seconds
fi

# Display message or play sound
if [ -n "$message" ]; then
    echo "$message"
    echo '>'
fi

if [ -n "$sound_file" ]; then
    if [ -f "$sound_file" ]; then
        # Check if the `play` command is available (install sox package if not available)
        command -v play >/dev/null 2>&1 || { echo >&2 "Error: 'play' command not found. Install sox package."; exit 1; }
        (play "$sound_file" >/dev/null 2>&1 &)  # Run play command in a subshell in the background
        echo '>'
    else
        echo "Error: Sound file not found."
        exit 1
    fi
fi

