import mysql.connector
import pandas as pd

def establish_sql_connection():
    ## note: for testing purposes, run on localhost
    db = mysql.connector.connect(
        host = "localhost",
        port = "8080",
        user = "root",
        password = "dsa3101",
        database = "secdb"
        )
    ## uncomment below for dockerised usage
    # db = mysql.connector.connect(
    #     host = "database",
    #     user = "root",
    #     password = "dsa3101",
    #     database = "secdb"
    #     )
    return db

establish_sql_connection()