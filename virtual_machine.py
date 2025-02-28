class VirtualMachine:
    def __init__(self, machine_id, clock_rate, port, peer_addresses):
        """
        Initialize a virtual machine with a given ID, clock rate, and peer addresses.
        
        Args:
            machine_id (int): The ID of this virtual machine
            clock_rate (int): The number of clock ticks per second (1-6)
            port (int): Port to listen on
            peer_addresses (list): List of (host, port) tuples for peer machines
        """
        print("TODO: Virt Machine class not implemented yet")

    def start(self):
        """Start the virtual machine."""
        print("TODO: start virtual machine not implemented yet")        

    def stop(self):
        """Stop the virtual machine."""
        print("TODDO: stop virtual machine not impl yet")    

    def _connect_to_peers(self):
        """Connect to peer machines."""
        pass


    def _listen_for_messages(self):
        pass
    
    def _handle_client_connection(self, client_socket, address):
        """Handle messages from a connected client."""
        pass 

    # ... etc. 

    def log_event(self, event_type, queue_length):
        """Log an event with current system time, queue length, and logical clock value."""
        print("TODO: logging of a machine not implemented yet")
    
    def log(self, message):
        """Write a message to the log file."""
        
        print("TODO: logging of a machine not implemented yet")
