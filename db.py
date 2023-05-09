## STANDARD MODULE IMPORTS
## -----------------------

import os
import sqlite3
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
SCHEMA_PATH = "\\db\\schema.sql"

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

def get_id(tablename, label): # TODO
    pass

def insert_subcats():
    '''get user-customised categories from csv'''
    conn, cursor = conn_init()
    # logger.info(begin("Getting subcategories from csv"))
    df = pd.read_csv("./db/cat.csv")
    # logger.info(success ("Grabbed %s subcategories from csv" % len(df.index)))
    df.to_sql("subcategories", conn, if_exists="replace")


    conn.close()
    


## MAIN ROUTINE
## ------------






