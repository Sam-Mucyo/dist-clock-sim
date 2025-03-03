# Engineering Notebook

## Overview of requirements 

Requirements for this distributed system were to make sure multiple virtual machines operate independently, communicate asynchronously, and maintain logical clocks to track causality.

Specifically, each machine needs to
- Runs at a unique clock rate (1-6 ticks per second)
- Communicates with other machines via TCP sockets
- Maintains a message queue for incoming messages
- Updates its logical clock based on internal events and message passing
- Logs all activities for post-simulation analysis 

## Thought Process  

### **Initial Design**  
We started by breaking down the problem into smaller components:  
1. **Virtual Machines**: Each machine needed to operate independently, with its own clock rate and logical clock.  
2. **Communication**: Machines needed to send and receive messages asynchronously.  
3. **Logical Clocks**: We needed to implement rules for updating logical clocks during internal events and message passing.  
4. **Logging**: To analyze the system's behavior, we decided to log all events (internal, send, receive) with timestamps and logical clock values.  

We chose TCP sockets for communication because they provide reliable, ordered message delivery, which is important for maintaining causality in the system.  We also considered using IPC or threads, but ultimately decided to use TCP.

We also decided to scope the project into 2 milestones:
For v1, we'd get something running in Python.
For v2, we thought of a potential extension, building a separate simulation in C++

### **Challenges**  

1. **Clock Synchronization**:  
One challenge was ensuring that logical clocks were updated correctly during message passing was tricky. We needed to handle cases where a machine received a message with a lower logical clock value than its current state.  Our solution was that when  it receives a message, it updates its logical clock to the maximum of its current value and the received timestamp, then increments it by 1.  

2. **Asynchronous Communication**:  
One challenge was managing asynchronous message sending and receiving without blocking the main thread. We used threading (Python module) to create separate threads for sending, receiving, and processing messages, so each machines can operate independently while still communicating with others.  

3. **Message Queue Management**:  
We also needed to handle incoming messages while processing internal events required careful coordination to avoid race conditions., so we used a thread-safe queue to store incoming messages instead of a list, that way the main processing loop could handle messages in the correct order.  

4. **Debugging and Logging**:  
We implemented detailed logging for every event, including timestamps, event types, queue lengths, and logical clock values. That way we could reconstruct the system's behavior during post-simulation analysis.  

## Lessons Learned  

   - Managing asynchronous communication introduced challenges like race conditions and deadlocks, so we had to use thread-safe data structures and careful synchronization

   - Debugging issues in a distributed system is a bit harder than in a single-threaded application b/c things are asynch; we found that detailed logging and visualization tools were essential for understanding the system's behavior. 

   - Scaling to a larger system would require optimizations like non-blocking I/O and more efficient message handling

## Future Work  
   - Add support for more complex communication patterns, such as multicast or broadcast messages
   - build out v2 in C++  