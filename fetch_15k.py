"""
Standalone quick downloader to pre-populate 'earthquakes.json' with 15,000 records.
Run once so you already have full data ready to demonstrate!
"""

import time
import json
import requests

def download_15k_earthquakes():
    base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2024-01-01&endtime=2024-03-01&minmagnitude=1.0"
    target = 15000
    batch_size = 1000
    offset = 1
    collected = []

    print(f"Downloading {target} earthquake records from USGS...")

    while len(collected) < target:
        url = f"{base_url}&limit={batch_size}&offset={offset}"
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                print(f"Failed with status: {resp.status_code}")
                break
            data = resp.json()
            features = data.get("features", [])
            if not features:
                print("No more features found.")
                break

            for item in features:
                props = item.get("properties", {})
                coords = item.get("geometry", {}).get("coordinates", [0.0, 0.0, 0.0])
                
                record = {
                    "id": str(item.get("id", "")),
                    "place": str(props.get("place", "Unknown Location")),
                    "magnitude": float(props.get("mag")) if props.get("mag") is not None else 0.0,
                    "time": int(props.get("time", 0)),
                    "depth": float(coords[2]) if len(coords) > 2 else 0.0,
                    "latitude": float(coords[1]) if len(coords) > 1 else 0.0,
                    "longitude": float(coords[0]) if len(coords) > 0 else 0.0,
                    "significance": int(props.get("sig", 0)),
                    "status": str(props.get("status", "automatic")),
                }
                collected.append(record)
                if len(collected) >= target:
                    break

            print(f"Fetched {len(collected)} / {target} records...")
            offset += batch_size
            time.sleep(0.2)

        except Exception as e:
            print("Error:", e)
            break

    with open("earthquakes.json", "w", encoding="utf-8") as f:
        json.dump(collected, f)
    print(f"Successfully saved {len(collected)} records to earthquakes.json!")

if __name__ == "__main__":
    download_15k_earthquakes()
