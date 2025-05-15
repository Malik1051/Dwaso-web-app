import sqlite3
import os

def init_db():
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # Read schema file
    with open('schema.sql', 'r') as f:
        schema = f.read()
    
    # Execute schema
    cursor.executescript(schema)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db() 