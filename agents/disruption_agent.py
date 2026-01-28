import pandas as pd
import time
from datetime import datetime
from agents.base_agent import BaseAgent

class DisruptionDetectionAgent(BaseAgent):
    def __init__(self, poll_interval=10):
        super().__init__("DisruptionDetectionAgent")
        self.poll_interval = poll_interval
        self.last_seen_delays = {}

    def run(self, flight_schedule_path, callback):
        """
        Continuously monitors flight_schedule.csv.
        Calculates delay as duration (arrival_utc - departure_utc).
        Passes ALL current disruptions to the callback.
        """
        while True:
            try:
                df = pd.read_csv(flight_schedule_path)
                df['departure_utc'] = pd.to_datetime(df['departure_utc'])
                df['arrival_utc'] = pd.to_datetime(df['arrival_utc'])
                df['calculated_delay'] = (df['arrival_utc'] - df['departure_utc']).dt.total_seconds() / 60

                current_disruptions = []

                for _, row in df.iterrows():
                    flight = row['flight']
                    delay = row['calculated_delay']

                    if delay >= 120:
                        event = {
                            "flight": flight,
                            "station": row['origin'],
                            "delay_minutes": delay,
                            "disruption_type": "DELAY",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        current_disruptions.append(event)

                # Pass the full list of active disruptions to the orchestrator
                callback(current_disruptions)

            except Exception as e:
                print(f"Error reading or processing schedule: {e}")

            time.sleep(self.poll_interval)
