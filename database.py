import datetime
import sqlite3
import json
#import logger

db_file = "zalohaDB/invio_pods.db"

def create_connection(db_file=db_file):
    conn = sqlite3.connect(db_file)
    conn.cursor().execute('''
                          CREATE TABLE IF NOT EXISTS pods (
                            date TEXT NOT NULL,
                            filename TEXT NOT NULL,
	                        invio_number TEXT NOT NULL,
                            gw_number TEXT NOT NULL,
                            sent_by_email BOOLEAN)
                          ''')
    conn.commit()
    return conn

def select_gw_number(invio_number):
    conn = create_connection()
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    #cursor.execute("SELECT json_object('gw_cislo', gw_number,'invio_number', invio_number ) FROM pods WHERE sent_by_email = FALSE ")
    cursor.execute("SELECT gw_number  FROM pods WHERE invio_number = ? ",(invio_number,))
    rows = cursor.fetchone()
    #res =[json.loads(x) for x in rows]
    #print(rows)
    return rows

def select_neposlane():
    conn = create_connection()
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    #cursor.execute("SELECT json_object('gw_cislo', gw_number,'invio_number', invio_number ) FROM pods WHERE sent_by_email = FALSE ")
    cursor.execute("SELECT invio_number FROM pods WHERE sent_by_email = FALSE")
    rows = cursor.fetchall()
    #res =[json.loads(x) for x in rows]
    #print(rows)
    return rows

def select_filenames():
    conn = create_connection()
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    #cursor.execute("SELECT json_object('gw_cislo', gw_number,'invio_number', invio_number ) FROM pods WHERE sent_by_email = FALSE ")
    cursor.execute("SELECT filename FROM pods")
    rows = cursor.fetchall()
    #res =[json.loads(x) for x in rows]
    #print(rows)
    return rows
     
def update_item_by_filename(filename, set_sent_by_email = False):
    # Establish a connection to the database
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE pods SET sent_by_email = ? WHERE filename = ?',((set_sent_by_email, filename)))
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def update_item(invio_number, set_sent_by_email = False):
    # Establish a connection to the database
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE pods SET sent_by_email = ? WHERE invio_number = ?',((set_sent_by_email, invio_number)))
    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def insert_item(values):
    # Establish a connection to the database
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM pods WHERE filename=?', (values[1],))
    if values != None and not cursor.fetchone():
        cursor.execute(
            'INSERT INTO pods (date, filename, invio_number, gw_number, sent_by_email) VALUES(?,?,?,?,?)', values)
        print("data vlozena")
    else:
        print("zaznam uz existuje")
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

#select_filenames()
