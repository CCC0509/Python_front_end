import sqlite3

conn = sqlite3.connect("datafile.db")  # create database
cursor = conn.cursor()

# create table
cursor.execute(
    """create table cash (transaction_id integer primary key, taiwanese_dollars integer, us_dollars real, note varchar(30), date_info date)""")

cursor.execute(
    """create table stock (transaction_id integer primary key, stock_id varchar(10), stock_num integer, stock_price real, processing_fee real, tax integer, date_info date)""")


conn.commit()
conn.close()
