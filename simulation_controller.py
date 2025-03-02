import random
import time
import signal
import sys
from virtual_machine import VirtualMachine

class SimulationController:
    def __init__(self, num_machines=3, base_port=5000, simulation_duration=60):
        """
        Initialize the simulation controller.
        
        Args:
            num_machines (int): Number of virtual machines to simulate
            base_port (int): Starting port number for the machines
            simulation_duration (int): Duration of simulation in seconds
        """
        self.num_machines = num_machines
        self.base_port = base_port
        self.simulation_duration = simulation_duration
        self.machines = []

        # NOTE: for v1, we will treat all virtual machines as running from same address
        # could also have been 'localhost'. we can extend this later in Milestone v2. 
        self.model_addr = '127.0.0.1'   
        
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
            clock_rate = random.randint(1, 6)  # Random clock rate between 1-6 ticks/second
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
                address = self.model_addr,
                clock_rate=clock_rate,
                port=port,
                peer_addresses=peer_addresses
            )
            self.machines.append(machine)
            
            print(f"  Machine {machine_id}: Port {port}, Clock Rate: {clock_rate} ticks/second")
    
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
    # Create and run the simulation
    print("=== Distributed System Simulation with Logical Clocks ===")
    
    sim = SimulationController(num_machines=3, simulation_duration=60)
    sim.initialize()
    sim.start()
