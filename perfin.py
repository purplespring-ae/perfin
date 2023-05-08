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
INPUT_DIR = ".\\raw\\new"
ARCHIVE_DIR = ".\\raw\\archive"
CSV_DIR = ".\\raw\\pf" # for combined CSV files

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

    def get_input_files():
        dfs = []
        for f in input_files:
            # read CSV using index_col=False to avoid CC misalignment
            df = pd.read_csv(f, index_col=False)
            df.columns = df.columns.str.strip()
            dfs.append(df)
            
        merged_df = pd.concat(dfs)
        return merged_df

    def standardise_input_data(df):
        # Standardise account name
        df["Account Name"] = df["Account Name"].replace(
            {"HOME": "HOME",
            "Saver": "SAVER",
            "'A W EVANS": 'CREDIT'})
        # Reformat: rectify duplicate indices
        df = df.reset_index(drop=True) 
        # Reformat: standardise and type Date
        df["Date"] = pd.to_datetime(df["Date"], format="mixed")

        return df
    
    def add_columns(df):
        # add columns for expense/income categorisation
            df["Type"] = "TBC"
            df["Category"] = "TBC"
            df["Sub-Category"] = "TBC"

            return df

    def format_tr_value(df):
        # Reformat: type Value
        df["Value"] = df["Value"].astype(float)
        # Reformat: add Debit and Credit columns
        df["Debit"] = ""
        df["Credit"] = ""
        # Reformat: Split "Value" into Dr Cr depending on if credit card
        is_cc = (df["Account Name"] == "CREDIT")
        is_pos = (df["Value"] > 0)
        is_neg = (df["Value"] < 0)
        df["Credit"] = np.where(is_cc & is_pos, df["Value"],"")
        df["Debit"] = np.where(is_cc & is_neg, abs(df["Value"]),"")
        df["Credit"] = np.where(~is_cc & is_pos, df["Value"],"")
        df["Debit"] = np.where(~is_cc & is_neg, abs(df["Value"]),"")
        return df

    def trim_input_bloat(df):
        # Reformat: trim bloat from Description
        df["Description"] = df["Description"].str.lstrip("'")
        # Reformat: drop unneeded columns
        df = df.drop(columns=["Value","Account Number"])
        return df    
 
    def merged_df_export(df):
        # save merged df to csv
        earliest_date = df["Date"].min().strftime(FNAME_DATE) 
        latest_date = df["Date"].max().strftime(FNAME_DATE)
        today_date = datetime.today().strftime(FNAME_DATE)
        logger.info("Transactions found for this date range: %s to %s", earliest_date, latest_date)
        fname = f"transactions_{earliest_date}_to_{latest_date}_imported_{today_date}"
        fpath = os.path.join(CSV_DIR,fname + ".csv")
        df.to_csv(fpath)
        return fpath
    
    def archive_processed_csv():
        # move iput csv to archive
        pass
        # for f in input_files:
        #     os.rename(f, os.path.join(ARCHIVE_DIR, os.path.basename(f) + ".csv"))

    df = get_input_files()
    df = standardise_input_data(df)
    df = add_columns(df)
    df = format_tr_value(df)
    df = trim_input_bloat(df)
    merged_csv = merged_df_export(df)
    print(merged_csv)



def categorise_transactions(merged_csv):
    df = pd.read_csv(merged_csv)

# MAIN ROUTINE

if __name__ == "__main__":
    # instantiate logger
    logger = perflog.logger(terminal_level=logging.DEBUG, file_level=0)

    # work with new data
    fpath_new = import_new_csv()
    # categorise_transactions(fpath_new)
