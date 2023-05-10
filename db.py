## STANDARD MODULE IMPORTS
## -----------------------

import os
import sqlite3
import csv
# import sqlalchemy
import pandas as pd
# import logging # TODO
# import perflog as lg

## LOCAL MODULE IMPORTS
## --------------------
# from perflog import logger as lg, success, begin, failed
# from perfin import logger

## GLOBAL VARIABLES
## ----------------

DB_PATH = ".\\db\\perfin-sqlite.db"
SCHEMA_PATH = ".\\db\\schema.sql"
SUBCATS_PATH = ".\\db\\cat.csv"

## DATABASE INIT FUNCTIONS
## -----------------------

def create_tables():
    pass

def conn_init():
    # logger.info(begin("Connecting to database"))
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        # logger.warning(failed("Database directory %s not found." % db_dir))
        os.makedirs(db_dir)
        # logger.warning(success("Created database directory %s" % db_dir))
    # logger.info(begin("Creating connection and cursor"))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # logger.info(success("Returning connection and cursor"))
    return conn, cursor

## UTILITY FUNCTIONS
## -----------------

def insert_transactions(df:pd.DataFrame):
    conn, cursor = conn_init()
    df.to_sql("transactions", conn, if_exists="append", index=False)
    conn.close()

def get_sc_id(label:str):
    conn, cursor = conn_init()

    conn.close()

def insert_subcats():
    '''insert new user-customised categories from csv to db'''
    conn, cursor = conn_init()
    sql_str =   """ SELECT label FROM subcategories
                """
    cursor.execute(sql_str)
    existing_subcats = [row[0] for row in cursor.fetchall()]

    with open(SUBCATS_PATH, "r") as subcats_csv:
        reader = csv.DictReader(subcats_csv)
        for row in reader:
            if row["label"] in existing_subcats:
                cursor.execute("UPDATE subcategories SET methods=?, amounts=?, descr_tells=? WHERE label=?",
                                (row["methods"], row["amounts"], row["descr_tells"], row["label"]))
            else:
                cursor.execute("INSERT INTO subcategories (label, category, methods, amounts, descr_tells) VALUES (?, ?, ?, ?, ?)",
                           (row["label"], row["category"], row["methods"], row["amounts"], row["descr_tells"]))


    conn.close()

    


## MAIN ROUTINE
## ------------






