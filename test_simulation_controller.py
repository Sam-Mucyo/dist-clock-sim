import pytest
import time
import sys
import signal
import random
from unittest.mock import patch, MagicMock

from simulation_controller import SimulationController
from virtual_machine import VirtualMachine


@pytest.fixture
def simulation_controller():
    """Fixture to create a basic simulation controller."""
    return SimulationController(num_machines=2, base_port=5000, simulation_duration=10)


def test_simulation_controller_init():
    """Test SimulationController initialization with default and custom parameters."""
    # Test with default parameters
    controller = SimulationController()
    assert controller.num_machines == 3
    assert controller.base_port == 5000
    assert controller.simulation_duration == 300
    assert controller.machines == []
    assert controller.model_addr == '127.0.0.1'
    
    # Test with custom parameters
    controller = SimulationController(num_machines=5, base_port=6000, simulation_duration=60)
    assert controller.num_machines == 5
    assert controller.base_port == 6000
    assert controller.simulation_duration == 60
    assert controller.machines == []
    assert controller.model_addr == '127.0.0.1'


@patch('random.randint')
def test_initialize(mock_randint, simulation_controller):
    """Test the initialize method of SimulationController."""
    # Mock random.randint to return predictable values
    mock_randint.side_effect = [3, 5]
    
    # Clear existing machines list and initialize the controller
    simulation_controller.machines = []
    simulation_controller.initialize()
    
    # Verify that VirtualMachine instances were created
    assert len(simulation_controller.machines) == 2
    
    # Check that machines have correct attributes
    assert simulation_controller.machines[0].machine_id == 1
    assert simulation_controller.machines[0].port == 5000
    assert simulation_controller.machines[0].clock_rate == 3
    assert simulation_controller.machines[0].address == '127.0.0.1'
    assert simulation_controller.machines[0].peers == [('127.0.0.1', 5001)]
    
    assert simulation_controller.machines[1].machine_id == 2
    assert simulation_controller.machines[1].port == 5001
    assert simulation_controller.machines[1].clock_rate == 5
    assert simulation_controller.machines[1].address == '127.0.0.1'
    assert simulation_controller.machines[1].peers == [('127.0.0.1', 5000)]


@patch('time.sleep')
def test_start_stop(mock_sleep, simulation_controller):
    """Test the start and stop methods of SimulationController."""
    # Create mock VirtualMachine instances
    mock_vm1 = MagicMock()
    mock_vm2 = MagicMock()
    simulation_controller.machines = [mock_vm1, mock_vm2]
    
    # Start the simulation
    simulation_controller.start()
    
    # Check if VMs were started
    mock_vm1.start.assert_called_once()
    mock_vm2.start.assert_called_once()
    
    # Check if sleep was called with correct duration
    mock_sleep.assert_called_with(10)  # Duration from fixture
    
    # Check if VMs were stopped
    mock_vm1.stop.assert_called_once()
    mock_vm2.stop.assert_called_once()


@patch('sys.exit')
def test_handle_interrupt(mock_exit, simulation_controller):
    """Test the _handle_interrupt method of SimulationController."""
    # Mock the stop method
    simulation_controller.stop = MagicMock()
    
    # Simulate interrupt
    simulation_controller._handle_interrupt(None, None)
    
    # Check if stop was called and sys.exit was called
    simulation_controller.stop.assert_called_once()
    mock_exit.assert_called_with(0)


@patch('signal.signal')
def test_signal_handler_registration(mock_signal):
    """Test that the signal handler is properly registered."""
    controller = SimulationController()
    mock_signal.assert_called_with(signal.SIGINT, controller._handle_interrupt)


def test_main_execution_path():
    """Test the main execution path when script is run directly."""
    # This test is simplified to check if the main block exists and contains expected code
    # Read the simulation_controller.py file
    with open('/Users/mirayu/CS 262 Problems/dist-clock-sim/simulation_controller.py', 'r') as f:
        content = f.read()
    
    # Check if the file contains a main block
    assert 'if __name__ == "__main__":' in content
    
    # Check if the main block contains the expected code
    main_block_exists = 'if __name__ == "__main__":' in content
    controller_instantiation = 'SimulationController(' in content
    initialize_call = '.initialize()' in content
    start_call = '.start()' in content
    
    # Assert that all expected elements are present
    assert main_block_exists, "Main block is missing"
    assert controller_instantiation, "Controller instantiation is missing"
    assert initialize_call, "Initialize call is missing"
    assert start_call, "Start call is missing"
