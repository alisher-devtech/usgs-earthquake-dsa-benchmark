import json
import time
from PyQt5.QtCore import QThread, pyqtSignal
import requests

DEFAULT_API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2024-01-01&endtime=2024-03-01&minmagnitude=1.0"

class ScraperThread(QThread):

    progress_signal = pyqtSignal(int, int)
    status_signal = pyqtSignal(str)
    batch_signal = pyqtSignal(list)
    finished_signal = pyqtSignal(list)

    def __init__(self, base_url=DEFAULT_API_URL, target_count=15000):
        super().__init__()
        self.base_url = base_url
        self.target_count = target_count

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

            while self.is_paused:
                if not self.is_running:
                    break
                time.sleep(0.2)

            if not self.is_running:
                break

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

                    if geom and "coordinates" in geom:
                        coords = geom.get("coordinates")
                    else:
                        coords = [0.0, 0.0, 0.0]

                    mag = props.get("mag")
                    if mag is not None:
                        mag_value = float(mag)
                    else:
                        mag_value = 0.0

                    if len(coords) > 2:
                        depth_value = float(coords[2])
                    else:
                        depth_value = 0.0

                    if len(coords) > 1:
                        lat_value = float(coords[1])
                    else:
                        lat_value = 0.0

                    if len(coords) > 0:
                        lon_value = float(coords[0])
                    else:
                        lon_value = 0.0

                    record = {
                        "id": str(item.get("id", "")),
                        "place": str(props.get("place", "Unknown Location")),
                        "magnitude": mag_value,
                        "time": int(props.get("time", 0)),
                        "depth": depth_value,
                        "latitude": lat_value,
                        "longitude": lon_value,
                        "significance": int(props.get("sig", 0)),
                        "status": str(props.get("status", "automatic")),
                    }

                    new_batch.append(record)
                    self.all_records.append(record)

                    if len(self.all_records) >= self.target_count:
                        break

                self.batch_signal.emit(new_batch)
                self.progress_signal.emit(
                    len(self.all_records), self.target_count
                )
                self.status_signal.emit(
                    f"Status: Fetched {len(self.all_records)} / {self.target_count} records"
                )

                offset += batch_size
                time.sleep(0.3)

            except Exception as e:
                self.status_signal.emit(f"Status: Network error: {str(e)}")
                break

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
