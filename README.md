## Distributed System Simulation with Logical Clocks

This project simulates a small asynchronous distributed system with multiple virtual machines running at different speeds, each maintaining their own logical clock according to Lamport's logical clock rules.

## Overview

The simulation creates multiple virtual machines that:
- Run at different clock rates (1-6 ticks per second)
- Communicate with each other via sockets
- Maintain message queues for incoming messages
- Update logical clocks based on internal events and message passing
- Log all activities to individual log files

## Project Structure

- `virtual_machine.py` - Implements the VirtualMachine class that models a single machine
- `controller.py` - Controls the initialization and execution of the simulation
- `log_analyzer.py` - Analyzes and visualizes the results of the simulation
- `logs/` - Directory where machine logs are stored

## How to Run

1. Start the simulation:
   ```
   python simulation_controller.py

   # TODO: fill in with chmod and ./ executable stuff
   ```
   This will create 3 virtual machines and run the simulation for 60 seconds.

2. After the simulation completes, analyze the results:
   ```
   python log_analyzer.py
   ```
   This will generate visualization plots and a text report in the `logs/` directory.

## Customization

You can modify the simulation parameters in `simulation_controller.py`:
- `num_machines` - Number of virtual machines to simulate
- `base_port` - Starting port number for machine communication
- `simulation_duration` - Duration of the simulation in seconds

## the Logs

Each machine creates a log file with the following columns:
- `Time` - System timestamp when the event occurred
- `Event` - Type of event (internal, send, receive)
- `Queue Length` - Current length of the message queue
- `Logical Clock` - Value of the logical clock after the event

## Visualization

#TODO


## Implementation Details

#TODO 
