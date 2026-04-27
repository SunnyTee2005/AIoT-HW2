# ⛅ CWA Temperature Forecast Web App (HW2)

This project fetches 7-day weather forecast data for Taiwan's main regions using the CWA Open Data API (F-A0010-001 endpoint), processes it into a SQLite database, and creates an interactive dashboard using Streamlit and Folium.

## Prerequisites
1. Ensure Python 3.8+ is installed.
2. Obtain a `CWA_API_KEY` from the Central Weather Administration (CWA).

## Execution Steps

1. Configure Environment:
Copy the `.env.example` file and rename it to `.env`.
   ```bash
   cp .env.example .env
   ```
Replace `YOUR_API_KEY_HERE` with your actual CWA API Key inside the `.env` file.

2. Activate the Virtual Environment (already installed):
   ```bash
   source .venv/bin/activate
   ```

3. Fetch Data and Populate Database:
Run the fetch script. It will connect to the CWA API and process the temperature extrema natively into `data.db` and output `weather_data.csv`.
   ```bash
   python fetch_data.py
   ```

4. Launch Streamlit Web App:
Run the Web UI using streamlit:
   ```bash
   streamlit run app.py
   ```

## Design Highlights
- Implements SSL request warning suppression and generic exception handling (`fetch_data.py`).
- Creates dual-pane layout (`app.py`):
    - **Map Tracking (Left)**: Calculates an approximated region temperature state for daily visualization.
    - **Raw Trends (Right)**: Extracts precise subset data per regional identifier for detailed Line charts (`min`, `max`) and DataFrame visualization matching visual references.
