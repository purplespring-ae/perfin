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

# GLOBAL VARIABLES
INPUT_DIR = "./raw/new"
ARCHIVE_DIR = "./raw/archive"
CSV_DIR = "./raw/pf" # for combined CSV files

FNAME_DATE = "%Y-%m-%d"

# INIT FUNCTIONS

def grab_input():
    '''Look in INPUT_DIR for .csv files, create dataframe, move csv to archive'''
    input_files = (
        [os.path.join(INPUT_DIR, fname) for fname in os.listdir(INPUT_DIR)
         if fname.endswith('.csv')]
        )
    if not input_files:
        logger.warning("No input files found.")
        return

    dfs = []
    for f in input_files:
        # read CSV using index_col=False to avoid CC misalignment
        df = pd.read_csv(f, index_col=False)
        df.columns = df.columns.str.strip()
        dfs.append(df)
        
    merged_df = pd.concat(dfs)
    merged_df = merged_df.reset_index(drop=True) # rectify duplicate indices
    merged_df["Date"] = pd.to_datetime(merged_df["Date"], format="mixed") # CC statement 

    earliest_date = merged_df["Date"].min().strftime(FNAME_DATE) 
    latest_date = merged_df["Date"].max().strftime(FNAME_DATE)
    today_date = datetime.today().strftime(FNAME_DATE)
    logger.info("Transactions found for this date range: %s to %s", earliest_date, latest_date)
    # save dataframe to csv - TODO: not needed?
    fname = f"transactions_{earliest_date}_to_{latest_date}_imported_{today_date}"
    merged_df.to_csv(os.path.join(CSV_DIR,fname))
    for f in input_files:
        # move iput csv to archive
        os.rename(f, os.path.join(ARCHIVE_DIR, os.path.basename(f)))

logger = perflog.logger(terminal_level=logging.DEBUG, file_level=0)

grab_input()
