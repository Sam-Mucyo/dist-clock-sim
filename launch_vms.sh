#!/bin/bash

# Script to launch multiple virtual machines in separate processes
# Usage: ./launch_vms.sh [num_machines] [duration] [min_clock] [max_clock] [internal_prob]

# Default values
NUM_MACHINES=${1:-3}
DURATION=${2:-60}
MIN_CLOCK=${3:-1}
MAX_CLOCK=${4:-6}
INTERNAL_PROB=${5:-0.7}
BASE_PORT=5000

# Create logs directory if it doesn't exist
mkdir -p logs

echo "=== Distributed System Simulation with Logical Clocks (Multi-Process) ==="
echo "Launching $NUM_MACHINES virtual machines in separate processes..."
echo "Simulation will run for $DURATION seconds"

# Generate random clock rates for each machine
declare -a CLOCK_RATES
for ((i=0; i<$NUM_MACHINES; i++)); do
    # Generate random clock rate between MIN_CLOCK and MAX_CLOCK
    CLOCK_RATES[$i]=$(( $RANDOM % ($MAX_CLOCK - $MIN_CLOCK + 1) + $MIN_CLOCK ))
done

# Generate peer lists for each machine
declare -a PEER_LISTS
for ((i=0; i<$NUM_MACHINES; i++)); do
    PEER_LIST=""
    for ((j=0; j<$NUM_MACHINES; j++)); do
        if [ $i -ne $j ]; then
            PEER_PORT=$(($BASE_PORT + $j))
            if [ -z "$PEER_LIST" ]; then
                PEER_LIST="127.0.0.1:$PEER_PORT"
            else
                PEER_LIST="$PEER_LIST,127.0.0.1:$PEER_PORT"
            fi
        fi
    done
    PEER_LISTS[$i]=$PEER_LIST
done

# Launch each VM in a separate process
VM_PIDS=()
for ((i=0; i<$NUM_MACHINES; i++)); do
    MACHINE_ID=$((i + 1))
    PORT=$((BASE_PORT + i))
    CLOCK_RATE=${CLOCK_RATES[$i]}
    PEER_LIST=${PEER_LISTS[$i]}
    
    echo "  Machine $MACHINE_ID: Port $PORT, Clock Rate: $CLOCK_RATE ticks/second"
    
    # Launch VM in background
    python virtual_machine.py \
        --machine-id $MACHINE_ID \
        --port $PORT \
        --clock-rate $CLOCK_RATE \
        --peer-list "$PEER_LIST" \
        --internal-prob $INTERNAL_PROB \
        --duration $DURATION &
    
    # Store the process ID
    VM_PIDS+=($!)
done

echo "All VMs launched. Simulation running for $DURATION seconds..."

# Wait for the specified duration
sleep $DURATION

# Send termination signal to all VM processes
echo "Stopping all virtual machines..."
for pid in "${VM_PIDS[@]}"; do
    kill $pid 2>/dev/null
done

# Wait for all processes to terminate
wait

echo "All machines stopped. Logs are available in the 'logs' directory."
