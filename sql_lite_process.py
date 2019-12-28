import sqlite3
from sqlite3 import Error
 
def sql_connection():
 
    try:
 
        con = sqlite3.connect('text_locations.db')
 
        return con
 
    except Error:
 
        print(Error)
 
def sql_table(con):
 
    cursorObj = con.cursor()
 
    cursorObj.execute("CREATE TABLE locations(id integer PRIMARY KEY AUTOINCREMENT, texts text, latitude float, longitude float)")
 
    con.commit()
 
# con = sql_connection()
# sql_table(con)

