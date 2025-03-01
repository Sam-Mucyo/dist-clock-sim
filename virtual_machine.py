# virtual_machine.py

import random
import time
import socket
import threading
import os
import queue
import json
from datetime import datetime

class Logger:
    def __init__(self, machine_id, clock_rate):
        self.machine_id = machine_id
        self.log_file = f"logs/machine_{machine_id}.log"
        os.makedirs("logs", exist_ok=True)
        
        with open(self.log_file, "w") as f:
            f.write(f"Machine {machine_id} initialized with clock rate {clock_rate}\n\n")
            f.write("Time,Event,Queue Length,Logical Clock\n")

    def log_record(self, event, queue_length, logical_clock):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"{timestamp},{event},{queue_length},{logical_clock}\n"
        with open(self.log_file, "a") as f:
            f.write(log_entry)

    def log_info(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"{timestamp}: Machine {self.machine_id}: {message}")

    def log_connection(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"{timestamp}: CONN_LOG: {message}\n"
        with open(self.log_file, "a") as f:
            f.write(log_entry)

class VirtualMachine:
    def __init__(self, machine_id, address, port, clock_rate):
        self.machine_id = machine_id
        self.address = address  # IP address or hostname of the machine
        self.clock_rate = clock_rate
        self.port = port
        self.peers = []  # List of (address, port) tuples
        self.logical_clock = 0
        self.message_queue = queue.Queue()  # Thread-safe queue
        self.logger = Logger(machine_id, clock_rate)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        self.socket.bind((self.address, self.port))  # Bind to the provided address
        self.running = False

    def add_peer(self, address, port):
        self.peers.append((address, port))

    def send(self, message, dest_address, dest_port):
        try:
            # Create a new socket for each send operation
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((dest_address, dest_port))
                s.sendall(json.dumps(message).encode())
                self.logical_clock += 1
                self.logger.log_record("send", self.message_queue.qsize(), self.logical_clock)
                self.logger.log_connection(f"Sent message to {dest_address}:{dest_port}: {message}")
        except Exception as e:
            self.logger.log_connection(f"Failed to send message to {dest_address}:{dest_port}: {e}")

    def receive(self):
        self.socket.listen(5)
        while self.running:
            try:
                client_socket, addr = self.socket.accept()
                data = client_socket.recv(1024).decode()
                if data:
                    message = json.loads(data)
                    received_time = message["logical_clock"]
                    self.logical_clock = max(self.logical_clock, received_time) + 1
                    self.message_queue.put(received_time)
                    self.logger.log_record("receive", self.message_queue.qsize(), self.logical_clock)
                client_socket.close()
            except Exception as e:
                self.logger.log_info(f"Error receiving message: {e}")

    def start(self):
        self.running = True
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        self.logger.log_info("Machine started")

    def stop(self):
        self.running = False
        self.socket.close()
        self.logger.log_info("Machine stopped")

    def run(self):
        self.start()
        while self.running:
            time.sleep(1 / self.clock_rate)
            
            if not self.message_queue.empty():
                received_time = self.message_queue.get()
                self.logical_clock = max(self.logical_clock, received_time) + 1
                self.logger.log_record("process", self.message_queue.qsize(), self.logical_clock)
            else:
                action = random.randint(1, 10)
                if action == 1:
                    # Send to the first peer
                    peer = self.peers[0]
                    self.send({"logical_clock": self.logical_clock}, peer[0], peer[1])
                elif action == 2:
                    # Send to the second peer
                    peer = self.peers[1]
                    self.send({"logical_clock": self.logical_clock}, peer[0], peer[1])
                elif action == 3:
                    # Send to both peers
                    for peer in self.peers:
                        self.send({"logical_clock": self.logical_clock}, peer[0], peer[1])
                else:
                    # Internal event
                    self.logical_clock += 1
                    self.logger.log_record("internal", self.message_queue.qsize(), self.logical_clock)

if __name__ == "__main__":
    # Use localhost for testing on a single machine
    address1 = "127.0.0.1"  # localhost
    address2 = "127.0.0.1"  # localhost
    address3 = "127.0.0.1"  # localhost

    # Initialize machines with their respective addresses
    vm1 = VirtualMachine(1, address1, 5001, 5)
    vm2 = VirtualMachine(2, address2, 5002, 5)
    vm3 = VirtualMachine(3, address3, 5003, 5)

    # Add peers
    vm1.add_peer(address2, 5002)
    vm1.add_peer(address3, 5003)
    vm2.add_peer(address1, 5001)
    vm2.add_peer(address3, 5003)
    vm3.add_peer(address1, 5001)
    vm3.add_peer(address2, 5002)

    # Start machines
    vm1.start()
    vm2.start()
    vm3.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Gracefully stop machines on keyboard interrupt
        vm1.stop()
        vm2.stop()
        vm3.stop()