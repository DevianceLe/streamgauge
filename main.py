##############################
# Stream Gauge Backend       #
# v2.0a1                     #
##############################

import sqlite3
import subprocess
import time

# Define the sleep loop timer
minutes = 15

# Where to save the database
weatherdb = './db/weather.db'

# Function to clear console screen
def clear_screen():
    print(chr(27) + "[2J")

# Function to initialize the database
def initialize_db():
    conn = sqlite3.connect(weatherdb)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to execute scripts with weather codes
def execute_scripts_with_codes():
    conn = sqlite3.connect(weatherdb)
    cursor = conn.cursor()
    cursor.execute('SELECT code FROM weather_codes')
    codes = cursor.fetchall()

    if not codes:
        print("No weather codes found in the database.")
    else:
        for code in codes:
            code = code[0].strip()
            print(f"Executing script with code: {code}")
            subprocess.run(['python', 'fetcher.py', '--gauge', code])

    conn.close()

# Function to insert weather code
def insert_weather_code(code, description):
    conn = sqlite3.connect(weatherdb)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO weather_codes (code, description) VALUES (?, ?)', (code, description))
    conn.commit()
    print(f"Added weather code '{code}' with description '{description}' to the database.")
    conn.close()

# Function to edit weather code
def edit_weather_code():
    conn = sqlite3.connect(weatherdb)
    cursor = conn.cursor()
    code_id = input("Enter ID of the weather code you want to edit: ")
    new_code = input("Enter new weather code (leave blank to keep existing): ").strip()
    new_description = input("Enter new description (leave blank to keep existing): ").strip()

    cursor.execute('SELECT code, description FROM weather_codes WHERE id=?', (code_id,))
    row = cursor.fetchone()

    if not row:
        print(f"Error: Weather code with ID {code_id} not found.")
        conn.close()
        return

    current_code, current_description = row

    if new_code:
        current_code = new_code
    if new_description:
        current_description = new_description

    cursor.execute('UPDATE weather_codes SET code=?, description=? WHERE id=?', (current_code, current_description, code_id))
    conn.commit()
    print(f"Updated weather code with ID {code_id}.")
    conn.close()

# Function to delete weather code
def delete_weather_code():
    conn = sqlite3.connect(weatherdb)
    cursor = conn.cursor()
    code_id = input("Enter ID of the weather code you want to delete: ")

    cursor.execute('SELECT code FROM weather_codes WHERE id=?', (code_id,))
    row = cursor.fetchone()

    if not row:
        print(f"Error: Weather code with ID {code_id} not found.")
        conn.close()
        return

    cursor.execute('DELETE FROM weather_codes WHERE id=?', (code_id,))
    conn.commit()
    print(f"Deleted weather code with ID {code_id}.")
    conn.close()

# Function to list all weather codes
def list_weather_codes():
    conn = sqlite3.connect(weatherdb)
    cursor = conn.cursor()
    cursor.execute('SELECT id, code, description FROM weather_codes')
    codes = cursor.fetchall()

    if not codes:
        print("No weather codes found.")
    else:
        print("Weather Codes:")
        for code in codes:
            print(f"ID: {code[0]}, Code: {code[1]}, Description: {code[2]}")

    conn.close()

# Function to add weather code
def add_weather_code():
    code = input("Enter weather code: ").strip()
    description = input("Enter description: ").strip()
    insert_weather_code(code, description)

# Main function to run the script
def main():
    clear_screen()
    print("------------------------")
    print("-STREAM GAUGE BACKEND  -")
    print("------------------------")
    print("-Developed by Deviance -")
    print("------------------------")
    
    initialize_db()  # Ensure the database is initialized
    
    while True:
        print("\nMenu:")
        print("1. Add Weather Code")
        print("2. Edit Weather Code")
        print("3. Delete Weather Code")
        print("4. List All Weather Codes")
        print("5. Start Execution Loop")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")
        if choice == '1':
            add_weather_code()
        elif choice == '2':
            edit_weather_code()
        elif choice == '3':
            delete_weather_code()
        elif choice == '4':
            list_weather_codes()
        elif choice == '5':
            print("Starting execution loop. Press Ctrl+C to stop.")
            try:
                while True:
                    execute_scripts_with_codes()
                    time.sleep(minutes * 60)
            except KeyboardInterrupt:
                print("\nExecution loop stopped.")
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")
    print("Exiting program.")

if __name__ == "__main__":
    main()
