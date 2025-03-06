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
    def __init__(self, machine_id, address, port, clock_rate, peer_addresses, internal_event_prob=0.7):
        """
        Initialize a virtual machine.
        
        Args:
            machine_id (int): Unique identifier for this machine
            address (str): IP address or hostname of the machine
            port (int): Port number for this machine
            clock_rate (int): Clock rate in ticks per second
            peer_addresses (list): List of (address, port) tuples for peer machines
            internal_event_prob (float): Probability of an event being internal (0.0-1.0)
        """
        self.machine_id = machine_id
        self.address = address  # IP address or hostname of the machine
        self.clock_rate = clock_rate
        self.port = port
        self.peers = peer_addresses  # List of (address, port) tuples
        self.internal_event_prob = internal_event_prob
        self.logical_clock = 0
        self.message_queue = queue.Queue()  # Thread-safe queue
        self.logger = Logger(machine_id, clock_rate)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address
        self.socket.bind((self.address, self.port))  # Bind to the provided address
        self.running = threading.Event()
        self.receive_thread = None
        self.run_thread = None

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
        while self.running.is_set():
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
                if self.running.is_set():
                    self.logger.log_info(f"Error receiving message: {e}")

    def start(self):
        self.running.set()
        self.receive_thread = threading.Thread(target=self.receive)
        self.run_thread = threading.Thread(target=self.run)
        self.receive_thread.start()
        self.run_thread.start()
        self.logger.log_info("Machine started")

    def stop(self):
        self.running.clear()
        self.socket.close()
        if self.receive_thread:
            self.receive_thread.join()
        if self.run_thread:
            self.run_thread.join()
        self.logger.log_info("Machine stopped")

    def run(self):
        while self.running.is_set():
            time.sleep(1 / self.clock_rate)
            
            if not self.message_queue.empty():
                received_time = self.message_queue.get()
                self.logical_clock = max(self.logical_clock, received_time) + 1
                self.logger.log_record("process", self.message_queue.qsize(), self.logical_clock)
            else:
                # Calculate thresholds based on internal_event_prob
                # For example, if internal_event_prob is 0.7, then 70% of events should be internal
                # and 30% should be message sends (10% to peer1, 10% to peer2, 10% to both)
                send_threshold = int((1 - self.internal_event_prob) * 100)
                send_to_first_threshold = int(send_threshold / 3)
                send_to_second_threshold = int(send_threshold / 3) * 2
                
                action = random.randint(1, 100)
                if action <= send_to_first_threshold:
                    # Send to the first peer
                    peer = self.peers[0]
                    self.send({"logical_clock": self.logical_clock}, peer[0], peer[1])
                elif action <= send_to_second_threshold:
                    # Send to the second peer
                    peer = self.peers[1]
                    self.send({"logical_clock": self.logical_clock}, peer[0], peer[1])
                elif action <= send_threshold:
                    # Send to both peers
                    for peer in self.peers:
                        self.send({"logical_clock": self.logical_clock}, peer[0], peer[1])
                else:
                    # Internal event
                    self.logical_clock += 1
                    self.logger.log_record("internal", self.message_queue.qsize(), self.logical_clock)