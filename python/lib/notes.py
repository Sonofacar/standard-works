import sqlite3
import os

def initialize(location):
    path = os.path.join(location,'notes.sql')
    con = sqlite3.Connection(path)
    phrase = 'CREATE TABLE IF NOT EXISTS notes (start INTEGER, end INTEGER, tags TEXT, text TEXT);'
    con.execute(phrase)
