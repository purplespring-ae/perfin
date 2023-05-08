import logging
import os
from datetime import datetime

LOG_DIR = "./log"

def logger(terminal_level=logging.INFO, file_level=logging.DEBUG):
    '''Set up terminal and file logging handlers'''

    # Check for dir and create if not found
    if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

    # Set up master logger
    master = logging.getLogger(__name__)
    master.setLevel(logging.DEBUG) # DEBUG,INFO,WARNING,ERROR,CRITICAL

    # Set up formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Set up terminal handler and add to logger
    if terminal_level:
        terminal_handler = logging.StreamHandler()
        terminal_handler.setLevel(terminal_level)
        terminal_handler.setFormatter(formatter)
        master.addHandler(terminal_handler)

    # Set up file handler and add to logger
    if file_level:
        log_file = os.path.join(LOG_DIR,f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log")
        file_handler = logging.FileHandler(log_file, "w")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        master.addHandler(file_handler)

    return master

def clear_files():
    '''Deletes .log files in the logging directory'''
    # TODO: Add parameters from_date and to_date=today to allow clearing of old logs
    if os.path.exists(LOG_DIR):
        for file in os.listdir(LOG_DIR):
            if file.endswith(".log"):
                os.remove(os.path.join(LOG_DIR,file))

def begin(message):
    return "Begin: " & message & "." if message[-1:] == "." else ""

def success(message):
    return "Success: " & message & "." if message[-1:] == "." else ""

def failed(message):
    return "Failure: " & message & "." if message[-1:] == "." else ""