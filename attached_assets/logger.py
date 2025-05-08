# logger.py - Simple logging for system events

from datetime import datetime

def log_event(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('logs/system_events.log', 'a') as log_file:
        log_file.write(f'[{timestamp}] {message}\n')
