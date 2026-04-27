import os
import sqlite3
import requests
import pandas as pd
from dotenv import load_dotenv

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_and_store_data():
    load_dotenv()
    
    # Try to get API key from local .env first
    api_key = os.getenv("CWA_API_KEY")
    
    # If not found locally, try to get it from Streamlit Cloud Secrets
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("CWA_API_KEY")
        except Exception:
            pass
            
    if not api_key:
        print("Error: Please set CWA_API_KEY in your .env file or Streamlit Secrets.")
        return False

    url = f"https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization={api_key}&downloadType=WEB&format=JSON"
    
    print("Fetching data from CWA API...")
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return False

    parsed_data = []
    
    try:
        locations = data.get("cwaopendata", {}).get("resources", {}).get("resource", {}).get("data", {}).get("agrWeatherForecasts", {}).get("weatherForecasts", {}).get("location", [])
    except Exception:
        locations = []

    if not locations:
        print("No location data found in the response.")
        return False

    target_regions = ["北部地區", "中部地區", "南部地區", "東北部地區", "東部地區", "東南部地區"]
    
    for loc in locations:
        region_name = loc.get("locationName")
        if region_name in target_regions:
            weather_elements = loc.get("weatherElements", {})
            mint_daily = weather_elements.get("MinT", {}).get("daily", [])
            maxt_daily = weather_elements.get("MaxT", {}).get("daily", [])
            
            # Map by date to easily match min/max
            date_map = {}
            for day in mint_daily:
                date_map[day["dataDate"]] = {"mint": day.get("temperature")}
                
            for day in maxt_daily:
                if day["dataDate"] in date_map:
                    date_map[day["dataDate"]]["maxt"] = day.get("temperature")
                    
            for date_str, temps in date_map.items():
                if "mint" in temps and "maxt" in temps:
                    try:
                        parsed_data.append({
                            "regionName": region_name,
                            "dataDate": date_str,
                            "mint": int(temps["mint"]),
                            "maxt": int(temps["maxt"])
                        })
                    except ValueError:
                        continue

    if not parsed_data:
        print("Data extraction failed, no valid matching region records parsed.")
        return False

    df = pd.DataFrame(parsed_data)
    
    # Clean duplicates keeping min MinT and max MaxT per day per region, or first value if identical dates
    df = df.groupby(['regionName', 'dataDate'], as_index=False).agg({'mint': 'min', 'maxt': 'max'})

    # SQLite
    db_name = "data.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TemperatureForecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regionName TEXT,
            dataDate TEXT,
            mint INTEGER,
            maxt INTEGER
        )
    ''')
    cursor.execute("DELETE FROM TemperatureForecasts")
    
    # Insert Data
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO TemperatureForecasts (regionName, dataDate, mint, maxt)
            VALUES (?, ?, ?, ?)
        ''', (row['regionName'], row['dataDate'], row['mint'], row['maxt']))
        
    conn.commit()
    conn.close()
    
    # Export to CSV
    csv_file = "weather_data.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    
    print(f"Success! Fetched {len(df)} records.")
    print(f"Data saved to {db_name} and {csv_file}")
    
    # Brief test query as required by the assignment
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    print("\n--- DB Check: All Regions in Database ---")
    cursor.execute("SELECT DISTINCT regionName FROM TemperatureForecasts")
    regions_in_db = [row[0] for row in cursor.fetchall()]
    print(", ".join(regions_in_db))
    
    print("\n--- DB Check: 中部地區 (Central Region) Records ---")
    cursor.execute("SELECT * FROM TemperatureForecasts WHERE regionName='中部地區'")
    central_records = cursor.fetchall()
    for rec in central_records:
        print(rec)
        
    conn.close()
    return True

if __name__ == "__main__":
    fetch_and_store_data()
