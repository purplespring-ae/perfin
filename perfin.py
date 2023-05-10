## STANDARD MODULE IMPORTS
## -----------------------
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
# import sqlalchemy
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
        df["Imported Date"] = datetime.today().strftime(FNAME_DATE)
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

        # Remove commas from Description which may confuse csv or sql and compact spacing
        df["Description"] = df["Description"].replace({
            ",": " ",
            "   ": " ",
            "  ": " "}
            )

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
        df["Debit"] = np.where((cc_mask & pos_mask) | (~cc_mask & neg_mask), abs(df["Value"]), np.nan)
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
 
    def rename_order_columns(df):
        logger.debug(begin("Renaming and reordering columns to match database."))
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
            "Balance",
            "Imported Date"
        ]
        df = df.reindex(columns=column_order)
        df = df.rename(columns={
            "Date": "date",
            "Method": "method",
            "Description": "description",
            "Type": "type",
            "Category": "category",
            "Sub-Category": "subcategory",
            "Debit": "debit",
            "Credit": "credit",
            "Account Name": "account",
            "Balance": "balance",
            "Imported Date":"imported_date"
        })
        logger.debug(success("Done matching columns to db"))
        return df

    def archive_processed_csv(fpaths):
        logger.info("Archiving processed .csv files")
        # move iput csv to archive
        for f in fpaths:
            new_path = os.path.join(ARCHIVE_DIR, os.path.basename(f))
            logger.debug("Renaming %s to %s" % (f, new_path))
            os.rename(f, new_path)
        logger.info(success("Done - Moved %s files" % len(fpaths)))

    df = merge_input_files(input_files)
    df = add_columns(df)
    df = standardise_input_data(df)
    df = double_entry_from_value(df)
    df = trim_input_bloat(df)
    df = rename_order_columns(df)
    # merged_csv = merged_df_export(df)
    archive_processed_csv(input_files)
    db.insert_transactions(df)

def get_subcats():
    pass


## UTILITY FUNCTIONS
## -----------------

def categorise_transactions(df_sc, df_tn):
    # add columns for suggested category and subcategory
    df_tn["suggest_sc"] = ""

## MAIN ROUTINE
## ------------

# instantiate logger
logger = lg(terminal_level=logging.DEBUG, file_level=0)

if __name__ == "__main__":

    # connect to db and config
    conn, cursor = db.conn_init()
    with open("db/schema.sql") as schema:
        commands = schema.read()
        cursor.executescript(commands)
    
    # work with new data
    fpath_new = import_new_csv()

    # categorise transactions
    db.insert_subcats()
    # db.get_sc_id("")
    # df_sc = get_subcats()
    # df_tn = pd.read_sql("SELECT * FROM transactions", conn)

    # categorise_transactions(df_sc, df_tn)
