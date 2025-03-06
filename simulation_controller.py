import random
import time
import signal
import sys
import argparse
from virtual_machine import VirtualMachine


class SimulationController:
    def __init__(self, num_machines=3, base_port=5000, simulation_duration=60, 
                 clock_rate_min=1, clock_rate_max=6, internal_event_prob=0.7):
        """
        Initialize the simulation controller.

        Args:
            num_machines (int): Number of virtual machines to simulate
            base_port (int): Starting port number for the machines
            simulation_duration (int): Duration of simulation in seconds
            clock_rate_min (int): Minimum clock rate (ticks/second)
            clock_rate_max (int): Maximum clock rate (ticks/second)
            internal_event_prob (float): Probability of an event being internal (0.0-1.0)
        """
        self.num_machines = num_machines
        self.base_port = base_port
        self.simulation_duration = simulation_duration
        self.clock_rate_min = clock_rate_min
        self.clock_rate_max = clock_rate_max
        self.internal_event_prob = internal_event_prob
        self.machines = []

        # NOTE: for v1, we will treat all virtual machines as running from same address
        # could also have been 'localhost'. we can extend this later in Milestone v2.
        self.model_addr = "127.0.0.1"

        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def initialize(self):
        """Initialize the virtual machines."""
        print(f"Initializing {self.num_machines} virtual machines...")

        # Generate machine configurations
        machine_configs = []
        for i in range(self.num_machines):
            machine_id = i + 1
            port = self.base_port + i
            clock_rate = random.randint(
                self.clock_rate_min, self.clock_rate_max
            )  # Random clock rate between min-max ticks/second
            machine_configs.append((machine_id, port, clock_rate))

        # Create peer address lists for each machine
        for i, (machine_id, port, clock_rate) in enumerate(machine_configs):
            peer_addresses = []
            for j, (_, peer_port, _) in enumerate(machine_configs):
                if i != j:  # Skip self
                    peer_addresses.append((self.model_addr, peer_port))

            # Create and store the machine
            machine = VirtualMachine(
                machine_id=machine_id,
                address=self.model_addr,
                clock_rate=clock_rate,
                port=port,
                peer_addresses=peer_addresses,
                internal_event_prob=self.internal_event_prob,
            )
            self.machines.append(machine)

            print(
                f"  Machine {machine_id}: Port {port}, Clock Rate: {clock_rate} ticks/second"
            )

    def start(self):
        """Start the simulation."""
        print("Starting all virtual machines...")

        # Start each machine
        for machine in self.machines:
            machine.start()

        print(f"Simulation running for {self.simulation_duration} seconds...")

        try:
            # Run for the specified duration
            time.sleep(self.simulation_duration)
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user.")

        self.stop()

    def stop(self):
        """Stop all virtual machines."""
        print("Stopping all virtual machines...")

        for machine in self.machines:
            machine.stop()

        print("All machines stopped. Logs are available in the 'logs' directory.")

    def _handle_interrupt(self, sig, frame):
        """Handle keyboard interrupt (Ctrl+C)."""
        print("\nReceived interrupt signal. Shutting down...")
        self.stop()
        sys.exit(0)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Distributed System Simulation with Logical Clocks"
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        default=60,
        help="Set simulation duration in seconds (default: 60)",
    )
    parser.add_argument(
        "-m",
        "--machines",
        type=int,
        default=3,
        help="Set number of virtual machines (default: 3)",
    )
    parser.add_argument(
        "--min-clock",
        type=int,
        default=1,
        help="Minimum clock rate in ticks/second (default: 1)",
    )
    parser.add_argument(
        "--max-clock",
        type=int,
        default=6,
        help="Maximum clock rate in ticks/second (default: 6)",
    )
    parser.add_argument(
        "-p",
        "--internal-prob",
        type=float,
        default=0.7,
        help="Probability of an event being internal (0.0-1.0) (default: 0.7)",
    )

    args = parser.parse_args()

    DURATION = args.duration
    NUM_MACHINES = args.machines
    MIN_CLOCK = args.min_clock
    MAX_CLOCK = args.max_clock
    INTERNAL_PROB = args.internal_prob

    # Create and run the simulation
    print("=== Distributed System Simulation with Logical Clocks ===")

    sim = SimulationController(
        num_machines=NUM_MACHINES, 
        simulation_duration=DURATION,
        clock_rate_min=MIN_CLOCK,
        clock_rate_max=MAX_CLOCK,
        internal_event_prob=INTERNAL_PROB
    )
    sim.initialize()
    sim.start()
