## Overview

This project simulates a small asynchronous distributed system with multiple virtual machines running at different speeds, each maintaining their own logical clock according to Lamport's logical clock rules.

## Engineering Notebooks & Results

Design notebook: [`notebook.md`](https://github.com/Sam-Mucyo/dist-clock-sim/blob/main/notebook.md)

Other entries: 
- [Issues](https://github.com/Sam-Mucyo/dist-clock-sim/issues?q=is%3Aissue%20state%3Aclosed%20milestone%3A%22Functional%20v1%22)
- [Merged PRs](https://github.com/Sam-Mucyo/dist-clock-sim/pulls?q=is%3Apr+is%3Aclosed)

Results: [`analysis.ipynb`](https://github.com/Sam-Mucyo/dist-clock-sim/blob/main/analysis.ipynb)

## Rubric Breakdown
- [x] Multiple processes? `virtual_machine.py`, `simulation_controller.py`
- [x] Follow the specifications? `virtual_machine.py`, `simulation_controller.py`
- [x] Observations leading to conclusions? `analysis.ipynb`
- [x] Tried the described variations? `analysis.ipynb`
- [x] Bonus? `analysis.ipynb`

## Functionalities
The simulation creates multiple virtual machines that:
- Run at different clock rates (1-6 ticks per second)
- Communicate with each other via sockets
- Maintain message queues for incoming messages
- Update logical clocks based on internal events and message passing
- Log all activities to individual log files

## Project Structure

- `virtual_machine.py` - Implements the VirtualMachine class that models a single machine
- `simulation_controller.py` - Controls the initialization and execution of the model by running VMs
- `log_analyzer.py` - Analyzes and visualizes the results of the simulation
- `logs/` - Directory where machine logs are stored
- `test_simulation_controller.py` - unit tests
- `test_virtual_machine.py` - unit tests

## How to Run

After cloning the repo, you may need to use the `setup` script to setup the environment with required dependencies by running: 

```bash
chmod +x setup
./setup
```
Rest (running the model and generating results plot), following:
[`analysis.ipynb`](https://github.com/Sam-Mucyo/dist-clock-sim/blob/main/analysis.ipynb)
