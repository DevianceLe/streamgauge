##################
# Fetcher Script #
##################
dbfolder = './db/'
outfolder = './output/'

import requests
import json
import sqlite3
import argparse
import matplotlib.pyplot as plt
from datetime import datetime

# Function to fetch and store data in the database
def fetch_and_store_gauge_data(gauge_id):
    print("Fetching weather code " + gauge_id + ".")
    # URL to fetch the data from
    url = f"https://api.water.noaa.gov/nwps/v1/gauges/{gauge_id}"

    # Fetch the data from the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()
        
        # Display the parsed data - Debugging
        #print(json.dumps(data, indent=4))

        # Connect to SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect(dbfolder + gauge_id + '.db')
        cursor = conn.cursor()

        # Create tables if they don't exist and will save unused info for future version updates.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gauge_info (
                lid TEXT,
                usgsId TEXT,
                reachId TEXT,
                name TEXT,
                rfc_name TEXT,
                rfc_abbreviation TEXT,
                wfo_name TEXT,
                wfo_abbreviation TEXT,
                state_name TEXT,
                state_abbreviation TEXT,
                county TEXT,
                timeZone TEXT,
                latitude REAL,
                longitude REAL,
                observed_primary REAL,
                observed_primaryUnit TEXT,
                observed_secondary REAL,
                observed_secondaryUnit TEXT,
                forecast_primary REAL,
                forecast_primaryUnit TEXT,
                forecast_secondary REAL,
                forecast_secondaryUnit TEXT,
                flood_stageUnits TEXT,
                flood_flowUnits TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (lid, timestamp)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flood_categories (
                lid TEXT,
                category TEXT,
                stage REAL,
                flow REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (lid, category, timestamp),
                FOREIGN KEY (lid) REFERENCES gauge_info (lid)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historic_crests (
                lid TEXT,
                occurredTime TEXT,
                stage REAL,
                flow REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (lid, occurredTime, timestamp),
                FOREIGN KEY (lid) REFERENCES gauge_info (lid)
            )
        ''')

        # Insert data into gauge_info table
        cursor.execute('''
            INSERT INTO gauge_info (
                lid, usgsId, reachId, name, rfc_name, rfc_abbreviation, wfo_name, wfo_abbreviation,
                state_name, state_abbreviation, county, timeZone, latitude, longitude,
                observed_primary, observed_primaryUnit, observed_secondary, observed_secondaryUnit,
                forecast_primary, forecast_primaryUnit, forecast_secondary, forecast_secondaryUnit,
                flood_stageUnits, flood_flowUnits
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['lid'], data['usgsId'], data['reachId'], data['name'],
            data['rfc']['name'], data['rfc']['abbreviation'],
            data['wfo']['name'], data['wfo']['abbreviation'],
            data['state']['name'], data['state']['abbreviation'],
            data['county'], data['timeZone'], data['latitude'], data['longitude'],
            data['status']['observed']['primary'], data['status']['observed']['primaryUnit'],
            data['status']['observed']['secondary'], data['status']['observed']['secondaryUnit'],
            data['status']['forecast']['primary'], data['status']['forecast']['primaryUnit'],
            data['status']['forecast']['secondary'], data['status']['forecast']['secondaryUnit'],
            data['flood']['stageUnits'], data['flood']['flowUnits']
        ))

        # Insert data into flood_categories table
        for category, values in data['flood']['categories'].items():
            cursor.execute('''
                INSERT OR IGNORE INTO flood_categories (lid, category, stage, flow)
                VALUES (?, ?, ?, ?)
            ''', (
                data['lid'], category, values['stage'], values['flow']
            ))

        # Insert data into historic_crests table
        for crest in data['flood']['crests']['historic']:
            cursor.execute('''
                INSERT OR IGNORE INTO historic_crests (lid, occurredTime, stage, flow)
                VALUES (?, ?, ?, ?)
            ''', (
                data['lid'], crest['occurredTime'], crest['stage'], crest['flow']
            ))

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

        print("Saved")
        
        # Fetch and plot gauge data
        plot_gauge_data(gauge_id, data['name'])

    else:
        print(f"Failed to fetch data. HTTP Status code: {response.status_code}")

# Function to fetch gauge data from the database
def fetch_gauge_data(gauge_id):
    conn = sqlite3.connect(dbfolder + gauge_id + '.db')
    cursor = conn.cursor()

    # Fetch observed_primary from gauge_info table
    cursor.execute('''
        SELECT timestamp, observed_primary
        FROM gauge_info
    ''')

    results = cursor.fetchall()
    conn.close()

    # Return timestamps and observed_primary values
    timestamps = [result[0] for result in results]
    observed_primary = [result[1] for result in results]

    return timestamps, observed_primary

# Function to fetch flood stage values from the database
def fetch_flood_stages(gauge_id):
    conn = sqlite3.connect(dbfolder + gauge_id + '.db')
    cursor = conn.cursor()

    # Fetch flood stage values from flood_categories table
    cursor.execute('''
        SELECT timestamp, category, stage
        FROM flood_categories
        WHERE category IN ('action', 'minor', 'moderate', 'major')
    ''')

    results = cursor.fetchall()
    conn.close()

    # Initialize dictionaries to store timestamps and flood stages
    flood_stages = {
        'action': [],
        'minor': [],
        'moderate': [],
        'major': []
    }

    # Populate dictionaries with data
    for result in results:
        timestamp, category, stage = result
        if category in flood_stages:
            flood_stages[category].append(stage)

    return flood_stages

# Function to plot gauge data and save as PNG
def plot_gauge_data(gauge_id, gauge_name):
    timestamps, observed_primary = fetch_gauge_data(gauge_id)
    flood_stages = fetch_flood_stages(gauge_id)

    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, observed_primary, marker='o', linestyle='-', color='b', label='Observed Primary')

    for category, stages in flood_stages.items():
        plt.plot(timestamps, stages, linestyle='-', label=f'Flood {category.capitalize()}')

    plt.title(f'Observed Stream Readings for - {gauge_name}')
    plt.xlabel('Timestamp')
    plt.ylabel('Value')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.legend()

    # Annotate observed primary values on the plot
    for i, txt in enumerate(observed_primary):
        plt.annotate(txt, (timestamps[i], observed_primary[i]), textcoords="offset points", xytext=(0,5), ha='center')

    # Save the plot as PNG
    plt.savefig(f"{outfolder}{gauge_id}_gauge_data.png")

    # Optionally, display the plot
    # plt.show()

# Main function to get user input and call the fetch and store function
def main():
    parser = argparse.ArgumentParser(description="Fetch and store NOAA gauge data.")
    parser.add_argument('--gauge', required=True, help='Gauge ID to fetch data for')
    args = parser.parse_args()
    fetch_and_store_gauge_data(args.gauge)

if __name__ == "__main__":
    main()
