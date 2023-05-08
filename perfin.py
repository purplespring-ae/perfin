import os
import logging
# import csv
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from jupyter_dash import JupyterDash
from dash import dcc
from dash import html

# CLASS VARIABLES

# class Account():
   


# GLOBAL VARIABLES
INPUT_DIR = "./raw/new"
CSV_DIR = "./raw/pf" # for combined CSV files

# INIT FUNCTIONS
def logger_init(terminal_level=logging.INFO, file_level=logging.DEBUG):
    '''Set up terminal and file logging handlers'''

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
        log_file = f"log/{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log"
        file_handler = logging.FileHandler(log_file, "w")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        master.addHandler(file_handler)

    return master

def grab_input():
    '''Look in INPUT_DIR for .csv files and store as single csv in CSV_DIR'''
    input_files = (
        [os.path.join(INPUT_DIR, fname) for fname in os.listdir(INPUT_DIR)
         if fname.endswith('.csv')]
        )
    if not input_files:
        logger.warning("No input files found.")
        return

    dfs = []
    for f in input_files:
        df = pd.read_csv(f,index_col=False)
        df.columns = df.columns.str.strip()
        dfs.append(df)

        
    merged_df = pd.concat(dfs)
    merged_df.to_csv("test.csv")

    # earliest_date = merged_df["Date"].min().strftime("%Y-%M-%D")
    # latest_date = merged_df["Date"].max().strftime("%Y-%M-%D")
    # logger.info(earliest_date, latest_date)



logger = logger_init(terminal_level=logging.DEBUG, file_level=None)

grab_input()

# input_files =  list(os.listdir(INPUT_DIR))
# # print(list(input_files))
# for fname in input_files:
#     if fname[:4] == "HOME":
#         logger.info("Found %s.",fname)
#         fpath = os.path.join(INPUT_DIR, fname)
#         df = pd.read_csv(fpath)
#         # print(df)
