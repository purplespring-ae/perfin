## STANDARD MODULE IMPORTS
## -----------------------

import os
import sqlite3
import sqlalchemy
import logging
import perflog as lg

## LOCAL MODULE IMPORTS
## --------------------
from perflog import logger as lg, success, begin, failed

## GLOBAL VARIABLES
## ----------------

DB_PATH = ".\\db\\perfin-sqlite.db"
SCHEMA_PATH = "\\db\\schema.sql"

## DATABASE INIT FUNCTIONS
## -----------------------

def create_tables():
    pass

def conn_init():
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    return conn, cursor


## MAIN ROUTINE
## ------------






