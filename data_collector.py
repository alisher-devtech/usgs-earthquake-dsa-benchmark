"""
Data Collector Module:
Fetches 15,000+ Earthquake records from USGS API in batches.
Supports Start, Pause, Resume, Stop using a simple QThread.
"""

import json
import time
from PyQt5.QtCore import QThread, pyqtSignal
import requests

DEFAULT_API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2024-01-01&endtime=2024-03-01&minmagnitude=1.0"


class ScraperThread(QThread):
    # Signals for UI communication
    progress_signal = pyqtSignal(int, int)  # current_count, total_target
    status_signal = pyqtSignal(str)  # status text message
    batch_signal = pyqtSignal(list)  # batch of new records
    finished_signal = pyqtSignal(list)  # all records when done

    def __init__(self, base_url=DEFAULT_API_URL, target_count=15000):
        super().__init__()
        self.base_url = base_url
        self.target_count = target_count

        # Control flags (Very easy to rewrite)
        self.is_running = True
        self.is_paused = False
        self.all_records = []

    def pause(self):
        self.is_paused = True
        self.status_signal.emit("Status: Paused")

    def resume(self):
        self.is_paused = False
        self.status_signal.emit("Status: Resumed / Fetching...")

    def stop(self):
        self.is_running = False
        self.is_paused = False
        self.status_signal.emit("Status: Stopped by user")

    def run(self):
        self.all_records = []
        offset = 1
        batch_size = 1000

        self.status_signal.emit("Status: Starting download from USGS API...")

        while self.is_running and len(self.all_records) < self.target_count:
            # Handle Pause
            while self.is_paused:
                if not self.is_running:
                    break
                time.sleep(0.2)

            # Handle Stop
            if not self.is_running:
                break

            # Build URL with limit and offset
            url = f"{self.base_url}&limit={batch_size}&offset={offset}"

            try:
                response = requests.get(url, timeout=15)
                if response.status_code != 200:
                    self.status_signal.emit(
                        f"Status: API Error {response.status_code}"
                    )
                    break

                data = response.json()
                features = data.get("features", [])

                if not features:
                    self.status_signal.emit("Status: No more records available")
                    break

                new_batch = []
                for item in features:
                    props = item.get("properties", {})
                    geom = item.get("geometry", {})
                    coords = (
                        geom.get("coordinates", [0.0, 0.0, 0.0])
                        if geom
                        else [0.0, 0.0, 0.0]
                    )

                    # 9 clean attributes (Numbers and Strings)
                    record = {
                        "id": str(item.get("id", "")),
                        "place": str(props.get("place", "Unknown Location")),
                        "magnitude": (
                            float(props.get("mag"))
                            if props.get("mag") is not None
                            else 0.0
                        ),
                        "time": int(props.get("time", 0)),
                        "depth": (
                            float(coords[2]) if len(coords) > 2 else 0.0
                        ),  # km depth
                        "latitude": float(coords[1]) if len(coords) > 1 else 0.0,
                        "longitude": (
                            float(coords[0]) if len(coords) > 0 else 0.0
                        ),
                        "significance": int(props.get("sig", 0)),
                        "status": str(props.get("status", "automatic")),
                    }

                    new_batch.append(record)
                    self.all_records.append(record)

                    if len(self.all_records) >= self.target_count:
                        break

                # Send batch to table and update progress
                self.batch_signal.emit(new_batch)
                self.progress_signal.emit(
                    len(self.all_records), self.target_count
                )
                self.status_signal.emit(
                    f"Status: Fetched {len(self.all_records)} / {self.target_count} records"
                )

                offset += batch_size
                time.sleep(0.3)  # Polite API delay

            except Exception as e:
                self.status_signal.emit(f"Status: Network error: {str(e)}")
                break

        # Save data to local json file for instant reloads
        if self.all_records:
            try:
                with open("earthquakes.json", "w", encoding="utf-8") as f:
                    json.dump(self.all_records, f)
            except Exception:
                pass

        self.finished_signal.emit(self.all_records)
        self.status_signal.emit(
            f"Status: Finished! Total {len(self.all_records)} records loaded."
        )
