import sqlite3
import os

import tempfile
DB_PATH = os.path.join(tempfile.gettempdir(), 'waste_system.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create bins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            fill_level REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bin_id INTEGER NOT NULL,
            predicted_overflow INTEGER NOT NULL,
            prediction_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bin_id) REFERENCES bins (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def insert_bin(location, fill_level):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO bins (location, fill_level) VALUES (?, ?)',
        (location, fill_level)
    )
    conn.commit()
    bin_id = cursor.lastrowid
    conn.close()
    return bin_id

def update_bin(bin_id, fill_level):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE bins SET fill_level = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?',
        (fill_level, bin_id)
    )
    conn.commit()
    conn.close()

def get_all_bins():
    conn = get_db_connection()
    bins = conn.execute('SELECT * FROM bins').fetchall()
    conn.close()
    return [dict(ix) for ix in bins]

def get_bin(bin_id):
    conn = get_db_connection()
    bin_data = conn.execute('SELECT * FROM bins WHERE id = ?', (bin_id,)).fetchone()
    conn.close()
    return dict(bin_data) if bin_data else None

def insert_prediction(bin_id, predicted_overflow):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete old prediction for the bin and insert the new one
    cursor.execute('DELETE FROM predictions WHERE bin_id = ?', (bin_id,))
    cursor.execute(
        'INSERT INTO predictions (bin_id, predicted_overflow) VALUES (?, ?)',
        (bin_id, predicted_overflow)
    )
    conn.commit()
    conn.close()

def get_all_predictions():
    conn = get_db_connection()
    predictions = conn.execute('SELECT * FROM predictions').fetchall()
    conn.close()
    return [dict(ix) for ix in predictions]

if __name__ == '__main__':
    # Initialize DB if run directly
    init_db()
