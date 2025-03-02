import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


class LogAnalyzer:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.log_data = {}  # Dictionary to store parsed log data by machine ID

    def parse_logs(self):
        print(f"Parsing log files from {self.log_dir}...")

        for filename in os.listdir(self.log_dir):
            if filename.startswith("machine_") and filename.endswith(".log"):
                # Extract machine ID from filename
                machine_id = int(filename.split("_")[1].split(".")[0])

                # Read the log file
                log_path = os.path.join(self.log_dir, filename)

                # Skip header lines and parse the CSV part
                with open(log_path, "r") as file:
                    lines = file.readlines()

                header_end = 0
                for i, line in enumerate(lines):
                    if line.strip() == "Time,Event,Queue Length,Logical Clock":
                        header_end = i
                        break

                if header_end + 1 < len(lines):
                    data_lines = lines[header_end + 1 :]

                    # Parse data lines
                    parsed_data = []
                    for line in data_lines:
                        try:
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

                    # Convert to DataFrame
                    self.log_data[machine_id] = pd.DataFrame(parsed_data)
                    print(
                        f"  Parsed {len(parsed_data)} events for Machine {machine_id}"
                    )

    def analyze_clock_drift(self):
        """Analyze and visualize logical clock drift between machines."""
        if not self.log_data:
            print("No log data available. Run parse_logs() first.")
            return

        print("Analyzing logical clock drift...")

        # Create a plot
        plt.figure(figsize=(12, 8))

        # Plot logical clock values over time for each machine
        for machine_id, df in self.log_data.items():
            plt.plot(
                df["timestamp"],
                df["logical_clock"],
                label=f"Machine {machine_id}",
                marker="o",
                markersize=3,
                linestyle="-",
            )

        plt.title("Logical Clock Progression Over Time")
        plt.xlabel("Time")
        plt.ylabel("Logical Clock Value")
        plt.legend()
        plt.grid(True)

        # Save the plot
        plot_path = os.path.join(self.log_dir, "clock_drift.png")
        plt.savefig(plot_path)
        print(f"Clock drift plot saved to {plot_path}")

    def analyze_event_distribution(self):
        if not self.log_data:
            print("No log data available. Run parse_logs() first.")
            return

        print("Analyzing event distribution...")

        # Create a figure with subplots for each machine
        fig, axes = plt.subplots(
            len(self.log_data), 1, figsize=(10, 4 * len(self.log_data))
        )

        # If there's only one machine, wrap the axis in a list for consistent indexing
        if len(self.log_data) == 1:
            axes = [axes]

        for i, (machine_id, df) in enumerate(sorted(self.log_data.items())):
            event_counts = df["event_type"].value_counts()

            # Create a bar chart
            event_counts.plot(kind="bar", ax=axes[i])
            axes[i].set_title(f"Machine {machine_id} - Event Distribution")
            axes[i].set_ylabel("Count")
            axes[i].set_xlabel("Event Type")

            # Add count labels on bars
            for j, count in enumerate(event_counts):
                axes[i].text(j, count + 0.1, str(count), ha="center")

        plt.tight_layout()

        plot_path = os.path.join(self.log_dir, "event_distribution.png")
        plt.savefig(plot_path)
        print(f"Event distribution plot saved to {plot_path}")

    def analyze_queue_lengths(self):
        if not self.log_data:
            print("No log data available. Run parse_logs() first.")
            return

        print("Analyzing message queue lengths...")

        plt.figure(figsize=(12, 8))

        # Plot queue lengths over time for each machine
        for machine_id, df in self.log_data.items():
            plt.plot(
                df["timestamp"],
                df["queue_length"],
                label=f"Machine {machine_id}",
                marker=".",
                markersize=2,
                linestyle="-",
            )

        plt.title("Message Queue Length Over Time")
        plt.xlabel("Time")
        plt.ylabel("Queue Length")
        plt.legend()
        plt.grid(True)

        plot_path = os.path.join(self.log_dir, "queue_lengths.png")
        plt.savefig(plot_path)
        print(f"Queue length plot saved to {plot_path}")

    def generate_report(self):
        print("Generating full analysis report...")

        if not self.log_data:
            self.parse_logs()

        self.analyze_clock_drift()
        self.analyze_event_distribution()
        self.analyze_queue_lengths()

        # Create a summary report
        report_path = os.path.join(self.log_dir, "analysis_report.txt")
        with open(report_path, "w") as report_file:
            report_file.write("=== Distributed System Simulation Analysis ===\n\n")

            report_file.write("Machine Statistics:\n")
            report_file.write("-" * 50 + "\n")

            for machine_id, df in sorted(self.log_data.items()):
                report_file.write(f"Machine {machine_id}:\n")
                report_file.write(f"  Total events: {len(df)}\n")

                # Count by event type
                event_counts = df["event_type"].value_counts().to_dict()
                for event_type, count in event_counts.items():
                    report_file.write(f"  {event_type} events: {count}\n")

                # Clock statistics
                report_file.write(
                    f"  Final logical clock value: {df['logical_clock'].max()}\n"
                )
                report_file.write(
                    f"  Average queue length: {df['queue_length'].mean():.2f}\n"
                )
                report_file.write(
                    f"  Maximum queue length: {df['queue_length'].max()}\n"
                )
                report_file.write("\n")

            # Global observations
            report_file.write("Global Observations:\n")
            report_file.write("-" * 50 + "\n")

            # Calculate clock drift
            final_clocks = {
                machine_id: df["logical_clock"].max()
                for machine_id, df in self.log_data.items()
            }
            max_clock = max(final_clocks.values())
            min_clock = min(final_clocks.values())

            report_file.write(
                f"Maximum logical clock: {max_clock} (Machine {max(final_clocks, key=final_clocks.get)})\n"
            )
            report_file.write(
                f"Minimum logical clock: {min_clock} (Machine {min(final_clocks, key=final_clocks.get)})\n"
            )
            report_file.write(
                f"Clock drift between machines: {max_clock - min_clock}\n"
            )

            report_file.write("\nVisualization files:\n")
            report_file.write("- clock_drift.png - Logical clock progression\n")
            report_file.write(
                "- event_distribution.png - Distribution of event types\n"
            )
            report_file.write("- queue_lengths.png - Message queue lengths over time\n")

        print(f"Analysis report saved to {report_path}")


if __name__ == "__main__":
    analyzer = LogAnalyzer()
    analyzer.generate_report()
