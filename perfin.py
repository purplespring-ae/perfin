import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from jupyter_dash import JupyterDash
from dash import dcc
from dash import html
import perflog

# CLASS VARIABLES

# class Account():
   


# GLOBAL VARIABLES
INPUT_DIR = "./raw/new"
CSV_DIR = "./raw/pf" # for combined CSV files

# INIT FUNCTIONS

def grab_input():
    '''Look in INPUT_DIR for .csv files and store as single csv in CSV_DIR'''
    input_files = (
        [os.path.join(INPUT_DIR, fname) for fname in os.listdir(INPUT_DIR)
         if fname.endswith('.csv')]
        )
    if not input_files:
        perflog.warning("No input files found.")
        return

    dfs = []
    for f in input_files:
        # read CSV using index_col=False to avoid CC misalignment
        df = pd.read_csv(f, index_col=False)
        df.columns = df.columns.str.strip()
        dfs.append(df)

        
    merged_df = pd.concat(dfs)
    merged_df = merged_df.reset_index(drop=True) # rectify duplicate indices
    merged_df.to_csv("test.csv")

    # earliest_date = merged_df["Date"].min().strftime("%Y-%M-%D")
    # latest_date = merged_df["Date"].max().strftime("%Y-%M-%D")
    # logger.info(earliest_date, latest_date)



perflog = perflog.logger(terminal_level=logging.DEBUG, file_level=None)

grab_input()

# input_files =  list(os.listdir(INPUT_DIR))
# # print(list(input_files))
# for fname in input_files:
#     if fname[:4] == "HOME":
#         logger.info("Found %s.",fname)
#         fpath = os.path.join(INPUT_DIR, fname)
#         df = pd.read_csv(fpath)
#         # print(df)
