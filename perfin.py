## STANDARD MODULE IMPORTS
## -----------------------
import os
import logging
import configparser
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from jupyter_dash import JupyterDash
from dash import dcc
from dash import html

## LOCAL MODULE IMPORTS
## --------------------
from perflog import logger as lg, success, begin, failed

## CLASS VARIABLES
## --------------
class Account():
    def __init__(self, bank, label, csv_flag, is_credit) -> None:
        self.bank = bank
        self.label = label
        self.csv_flag = csv_flag
        self.is_credit = is_credit

class TransactionType():
    def __init__(self):
        pass

class TransactionCategory():
    def __init__(self, label:str, type:TransactionType):
        self.label = label
        self.type = type

class TransactionSubCategory(TransactionCategory):
    def __init__(self, label:str, type:TransactionType, category:TransactionCategory):
        super().__init__(label, type)
        self.category = category
        self.tells = [
            # strings to look for in ["Description"]
        ]

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
        # Reformat: rectify duplicate indices
        df = df.reset_index(drop=True) 
        # Reformat: standardise and type Date
        df["Date"] = pd.to_datetime(df["Date"], format="mixed")
        # Assign values to CC balance declaration
        mask = (df["Method"].isna()) & (df["Description"].str.contains("Balance")) & (df["Account Name"] == "CREDIT")
        df.loc[mask, "Method"] = "BAL"
        logger.debug(success("Done standardising data."))
        # Standardise CC transaction methods to TLA
        replace_methods = {"Purchase": "PUR", 
                        "Payment": "PAY", 
                        "Interest": "INT"}
        df["Method"] = df["Method"].replace(replace_methods)

        return df
    

    def format_tr_value(df):
        logger.debug(begin("Formatting Value column."))
        # type Value
        df["Value"] = df["Value"].astype(float)
        # Split "Value" into Dr Cr depending on if credit card
        is_cc = (df["Account Name"] == "CREDIT")
        is_pos = (df["Value"] > 0)
        is_neg = (df["Value"] < 0)
        df["Credit"] = np.where(is_cc & is_pos, df["Value"],"")
        df["Debit"] = np.where(is_cc & is_neg, abs(df["Value"]),"")
        df["Credit"] = np.where(~is_cc & is_pos, df["Value"],"")
        df["Debit"] = np.where(~is_cc & is_neg, abs(df["Value"]),"")
        logger.debug(success("Done formatting Value column."))
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
            new_path = os.path.join(ARCHIVE_DIR, os.path.basename(f) + ".csv")
            logger.debug("Renaming %s to %s" % f, new_path)
            os.rename(f, new_path)
        logger.info(success("Done -Moved %s files" % len(input_files)))

    df = merge_input_files(input_files)
    df = add_columns(df)
    df = standardise_input_data(df)
    df = format_tr_value(df)
    df = trim_input_bloat(df)
    df = reorder_columns(df)
    merged_csv = merged_df_export(df)
    # archive_processed_csv(input_files)
    return merged_csv

def categorise_transactions(merged_csv):
    df = pd.read_csv(merged_csv)
    

## MAIN ROUTINE
## ------------

if __name__ == "__main__":
    # instantiate logger
    logger = lg(terminal_level=logging.DEBUG, file_level=0)

    # work with new data
    fpath_new = import_new_csv()
    categorise_transactions(fpath_new)
