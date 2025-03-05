import os
import re
import pandas as pd
from datetime import datetime


class LogAnalyzer:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.log_data = {}  # Dictionary to store parsed log data by machine ID
        self.machine_rates = {}  # Dictionary to store clock rates by machine ID
        self.simulation_start_time = None
        self.simulation_end_time = None

    def parse_logs(self):
        print(f"Parsing log files from {self.log_dir}...")

        for filename in os.listdir(self.log_dir):
            if filename.startswith("machine_") and filename.endswith(".log"):
                # Extract machine ID from filename
                machine_id = int(filename.split("_")[1].split(".")[0])

                # Read the log file
                log_path = os.path.join(self.log_dir, filename)

                # Extract clock rate from the first line
                with open(log_path, "r") as file:
                    first_line = file.readline().strip()
                    rate_match = re.search(r"clock rate (\d+)", first_line)
                    if rate_match:
                        self.machine_rates[machine_id] = int(rate_match.group(1))

                    # Skip header lines and parse the CSV part
                    lines = file.readlines()

                csv_header_line = -1
                for i, line in enumerate(lines):
                    if line.strip() == "Time,Event,Queue Length,Logical Clock":
                        csv_header_line = i
                        break

                if csv_header_line >= 0 and csv_header_line + 1 < len(lines):
                    data_lines = lines[csv_header_line + 1 :]

                    # Parse data lines
                    parsed_data = []
                    for line in data_lines:
                        try:
                            # Skip lines that don't match expected CSV format
                            if ":" in line and not line.startswith(
                                "20"
                            ):  # Skip info log lines
                                continue

                            parts = line.strip().split(",")
                            if len(parts) == 4:
                                (
                                    timestamp_str,
                                    event_type,
                                    queue_length,
                                    logical_clock,
                                ) = parts

                                # Parse timestamp
                                timestamp = datetime.strptime(
                                    timestamp_str, "%Y-%m-%d %H:%M:%S.%f"
                                )

                                # Update simulation time range
                                if (
                                    self.simulation_start_time is None
                                    or timestamp < self.simulation_start_time
                                ):
                                    self.simulation_start_time = timestamp
                                if (
                                    self.simulation_end_time is None
                                    or timestamp > self.simulation_end_time
                                ):
                                    self.simulation_end_time = timestamp

                                # Parse other fields
                                queue_length = int(queue_length)
                                logical_clock = int(logical_clock)

                                parsed_data.append(
                                    {
                                        "timestamp": timestamp,
                                        "event_type": event_type,
                                        "queue_length": queue_length,
                                        "logical_clock": logical_clock,
                                    }
                                )
                        except Exception as e:
                            print(f"Error parsing line: {line.strip()} - {str(e)}")

                    # Convert to DataFrame and calculate clock jumps
                    df = pd.DataFrame(parsed_data)
                    if not df.empty:
                        df = df.sort_values("timestamp")
                        # Calculate jumps in logical clock values
                        df["clock_jump"] = df["logical_clock"].diff()
                        # First row will have NaN, fill with 1 (assuming first action always increments by 1)
                        df.loc[df["clock_jump"].isna(), "clock_jump"] = 1

                        self.log_data[machine_id] = df
                        print(
                            f"  Parsed {len(parsed_data)} events for Machine {machine_id} (Rate: {self.machine_rates.get(machine_id, 'Unknown')} ticks/sec)"
                        )

    def get_simulation_duration(self):
        if self.simulation_start_time and self.simulation_end_time:
            duration = (
                self.simulation_end_time - self.simulation_start_time
            ).total_seconds()
            return duration
        return 0

    def analyze_data(self):
        if not self.log_data:
            return "No log data available. Run parse_logs() first."

        summary = {}
        for machine_id, df in self.log_data.items():
            machine_summary = {
                "events_count": len(df),
                "avg_queue_length": df["queue_length"].mean(),
                "max_queue_length": df["queue_length"].max(),
                "avg_clock_jump": df["clock_jump"].mean(),
                "max_clock_jump": df["clock_jump"].max(),
                "internal_events": len(df[df["event_type"] == "internal"]),
                "send_events": len(df[df["event_type"] == "send"]),
                "receive_events": len(df[df["event_type"] == "receive"]),
            }
            summary[machine_id] = machine_summary

        return pd.DataFrame(summary).T
