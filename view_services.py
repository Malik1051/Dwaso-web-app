import sqlite3

def view_services():
    # Connect to database
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # Get table info
    print("=== Services Table Structure ===")
    cursor.execute("PRAGMA table_info(services)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"Column: {col[1]}, Type: {col[2]}, Required: {'Yes' if col[3] else 'No'}")
    
    print("\n=== Services Table Data ===")
    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()
    if services:
        for service in services:
            print(f"\nID: {service[0]}")
            print(f"Name: {service[1]}")
            print(f"Price: {service[2]}")
            print(f"Duration: {service[3]} hours")
            print(f"Description: {service[4]}")
            print(f"Image Path: {service[5]}")
            print(f"Created At: {service[6]}")
    else:
        print("No services found in the table.")
    
    conn.close()

if __name__ == '__main__':
    view_services() 