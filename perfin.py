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

class Account():
    def __init__(self, bank, label, csv_flag, is_credit) -> None:
        self.bank = bank
        self.label = label
        self.csv_flag = csv_flag
        self.is_credit = is_credit


# GLOBAL VARIABLES
INPUT_DIR = "./raw/new"
ARCHIVE_DIR = "./raw/archive"
CSV_DIR = "./raw/pf" # for combined CSV files

FNAME_DATE = "%Y-%m-%d"

# INIT FUNCTIONS

def import_new_csv():
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
    merged_df["Date"] = pd.to_datetime(merged_df["Date"], format="mixed")
    merged_df["Category"] = "Uncategorised"
    merged_df["Sub-Category"] = "Uncategorised"

    # save merged df to csv
    earliest_date = merged_df["Date"].min().strftime(FNAME_DATE) 
    latest_date = merged_df["Date"].max().strftime(FNAME_DATE)
    today_date = datetime.today().strftime(FNAME_DATE)
    logger.info("Transactions found for this date range: %s to %s", earliest_date, latest_date)
    fname = f"transactions_{earliest_date}_to_{latest_date}_imported_{today_date}"
    fpath = os.path.join(CSV_DIR,fname + ".csv")
    merged_df.to_csv(fpath)

    # move iput csv to archive merged
    for f in input_files:
        os.rename(f, os.path.join(ARCHIVE_DIR, os.path.basename(f) + ".csv"))
    
    return fpath

def categorise_transactions(merged_csv):
    pass

# MAIN ROUTINE

if __name__ == "__main__":
    # instantiate logger
    logger = perflog.logger(terminal_level=logging.DEBUG, file_level=0)

    # work with new data
    fpath_new = import_new_csv()
    categorise_transactions(fpath_new)
