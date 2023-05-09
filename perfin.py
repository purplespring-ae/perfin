## STANDARD MODULE IMPORTS
## -----------------------
import os
import logging
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from jupyter_dash import JupyterDash
from dash import dcc
from dash import html
import db

## LOCAL MODULE IMPORTS
## --------------------
from perflog import logger as lg, success, begin, failed

## CLASS VARIABLES
## --------------

## GLOBAL VARIABLES - FILE MANAGEMENT
## ----------------------------------
INPUT_DIR = ".\\raw\\new"
ARCHIVE_DIR = ".\\raw\\archive"
CSV_DIR = ".\\raw\\pf" # for combined CSV files

## GLOBAL VARIABLES - FORMATS
## --------------------------
FNAME_DATE = "%Y-%m-%d"

## INIT FUNCTIONS
## --------------

def import_new_csv():
    '''Look in INPUT_DIR for .csv files, create dataframe, move csv to archive'''
    input_files = (
        [os.path.join(INPUT_DIR, fname) for fname in os.listdir(INPUT_DIR)
        if fname.endswith('.csv')]
        )
    if not input_files:
        logger.warning(failed("No input files found."))
        return

    def merge_input_files(fnames):
        logger.info(begin("Getting input files"))
        dfs = []
        for f in fnames:
            # read CSV using index_col=False to avoid CC misalignment
            df = pd.read_csv(f, index_col=False)
            df.columns = df.columns.str.strip()
            dfs.append(df)
        merged_df = pd.concat(dfs)
        logger.info(success("Done getting input files - %s found" % len(dfs)))
        return merged_df

    def add_columns(df):
        logger.debug(begin("Adding columns."))
        # add columns for expense/income categorisation
        df["Method"] = df["Type"]
        df["Type"] = "TYPE_TBC"
        df["Category"] = "CAT_TBC"
        df["Sub-Category"] = "SUBCAT_TBC"
        # add double-entry columns
        df["Debit"] = ""
        df["Credit"] = ""
        logger.debug(success("Done adding columns."))
        return df

    def standardise_input_data(df):
        logger.debug(begin("Standardising data across sources"))
        # Standardise account name
        df["Account Name"] = df["Account Name"].replace(
            {"HOME": "HOME",
            "Saver": "SAVER",
            "'A W EVANS": 'CREDIT'})
        # Reformat: standardise and type Date
        ldate_mask = (df['Date'].str.contains(r"\d{2} \w{3} \d{4}"))
        sdate_mask = (df['Date'].str.contains(r"\d{2}/\d{2}/\d{4}"))
        df.loc[ldate_mask, 'Date'] = pd.to_datetime(df.loc[ldate_mask, 'Date'], format='%d %b %Y').dt.date
        df.loc[sdate_mask, 'Date'] = pd.to_datetime(df.loc[sdate_mask, 'Date'], format='%d/%m/%Y').dt.date
       
        # Handle null values for CC balance declaration method and Balance column
        mask_credit = (df["Account Name"] == "CREDIT")
        df.loc[mask_credit & (df["Method"].isna()) & (df["Description"].str.contains("Balance")), "Method"] = "BAL"
        print(df.loc[mask_credit & (df["Balance"].isna()), "Balance"])
        df.loc[mask_credit & (df["Balance"].isna()), "Balance"] = float("nan")

        # Standardise CC transaction methods to TLA
        replace_methods = {"Purchase": "PUR", 
                        "Payment": "PAY", 
                        "Interest": "INT"}
        df["Method"] = df["Method"].replace(replace_methods)
        logger.debug(success("Done standardising data."))

        # Reformat: rectify duplicate indices
        df = df.sort_values(by="Date", ascending=True)
        df = df.reset_index(drop=True) 

        return df
       
    def double_entry_from_value(df):
        logger.debug(begin("Formatting double entry columns."))
        df["Value"] = df["Value"].astype(float)

        cc_mask = (df["Account Name"] == "CREDIT")
        pos_mask = (df["Value"] > 0)
        neg_mask = (df["Value"] < 0)
        df["Debit"] = np.where((cc_mask & pos_mask) | (~cc_mask & neg_mask), df["Value"], np.nan)
        df["Credit"] = np.where((cc_mask & neg_mask) | (~cc_mask & pos_mask), abs(df["Value"]), np.nan)

        df[["Debit", "Credit"]] = df[["Debit", "Credit"]].fillna(np.nan)
        logger.debug(success("Done formatting double entry columns."))
        return df

    def trim_input_bloat(df):
        logger.debug(begin("Trimming input bloat"))
        # trim bloat from Description
        df["Description"] = df["Description"].str.lstrip("'")
        # drop unneeded columns
        df = df.drop(columns=["Value","Account Number"])
        logger.debug(success("Done trimming input bloat"))
        return df    
 
    def reorder_columns(df):
        logger.debug(begin("Reordering columns."))
        column_order = [
            "Date",
            "Method",
            "Description",
            "Type",
            "Category",
            "Sub-Category",
            "Debit",
            "Credit",
            "Account Name",
            "Balance"
        ]
        df = df.reindex(columns=column_order)
        logger.debug(success("Done reordering columns"))
        return df

    def merged_df_export(df):
        logger.info(begin("Exporting merged transactions dataframe to %s" % CSV_DIR))
        # save merged df to csv
        earliest_date = df["Date"].min().strftime(FNAME_DATE) 
        latest_date = df["Date"].max().strftime(FNAME_DATE)
        today_date = datetime.today().strftime(FNAME_DATE)
        logger.info("Transactions found for this date range: %s to %s", earliest_date, latest_date)
        fname = f"transactions_{earliest_date}_to_{latest_date}_imported_{today_date}"
        fpath = os.path.join(CSV_DIR,fname + ".csv")
        df.to_csv(fpath)
        logger.info(success("Done exporting transactions. Filepath: %s" % fpath))
        return fpath
    
    def archive_processed_csv(fpaths):
        logger.info("Archiving processed .csv files")
        # move iput csv to archive
        for f in input_files:
            new_path = os.path.join(ARCHIVE_DIR, os.path.basename(f))
            logger.debug("Renaming %s to %s" % (f, new_path))
            os.rename(f, new_path)
        logger.info(success("Done -Moved %s files" % len(input_files)))

    df = merge_input_files(input_files)
    df = add_columns(df)
    df = standardise_input_data(df)
    df = double_entry_from_value(df)
    df = trim_input_bloat(df)
    df = reorder_columns(df)
    merged_csv = merged_df_export(df)
    archive_processed_csv(input_files)
    return merged_csv

def categorise_transactions(merged_csv):
    df = pd.read_csv(merged_csv)
    

## MAIN ROUTINE
## ------------

if __name__ == "__main__":
    # instantiate logger
    logger = lg(terminal_level=logging.DEBUG, file_level=0)

    # connect to db
    conn, cursor = db.conn_init()

    # work with new data
    fpath_new = import_new_csv()
    # categorise_transactions(fpath_new)
