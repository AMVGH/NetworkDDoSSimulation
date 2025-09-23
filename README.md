# Network DDoS Simulation

**Author:** Alex Valentin

**Course:** CS 4632 Section W01

## Project Overview
The aim of this project is to analyze the impact of malicious network traffic on network systems. This area of study is extremely relevant to the overall network system domain, especially considering the rise of DDoS attacks against large enterprise services year-over-year. The results intend to explore how Distributed Denial of Service attacks (DDoS) impact server response time and the ability to serve legitimate network traffic, furthermore, how do safeguards such as load-balancing help reduce latency, improve throughput, and prevent server deterioration when under attack. This project will simulate legitimate and malicious network traffic, servers and server responses, and network performance degradation under load. Items outside the scope of this project and thus will not be included in the final simulation include the implementation of End-to-End security protocols (i.e.: TLS handshakes, firewalls, IDS/IPS).

## Installation Instructions and Usage Guide
### Installing Dependencies
Ensure that **Python Version 3.x** is installed on your local machine and have the required packages installed:

```bash
pip install simpy numpy matplotlib pytest
```

Dependency versions can be found in [requirements.txt](requirements.txt)

### Running the Simulation
In order to run the simulation clone the repository to your local environment and make sure all necessary dependencies are installed. After this, simply update the simulation configuration variables found in [SimulationExecutive.py](src/SimulationExecutive.py), once the configuration is set to your liking simply navigate to [main.py](src/main.py) and run the simulation. At the current moment, process outputs will be written to the terminal until the data collection logic is implemented.

## Project Status
At the current moment, class models and their properties have been implemented across the board except for certain class functions that drive logic for the simulation. Methods that handle simulation processes and communication between classes are in development, and are expected to show core simulation logic by the time of the M2 deliverable. There have been very minute changes from the original UML class diagrams, but no significant pivots from the initial proposal. Data collection logic is imperative to implement once the core simulation logic is finished, so that the user can visualize statistics regarding the simulation run.

## Architecture Overview
The main components in the simulation include the following: 
1. **BaseNetworkClient**
   - Base class that the two network clients derive from, no differences exist between what is implemented and what is proposed in the UML Class diagram. The client objects are still designed to generate requests to send to the Network.
2. **LegitimateNetworkClient**
   - Inherits everything from BaseNetworkClient, no differences exist between implementation and proposal.
3. **MaliciousNetworkClient**
   - Inherits everything from BaseNetworkClient, isEnabled and the functions to set and get the network state are not implemented at the moment and may potentially be discarded due to how processes will be handled in SimPy.
4. **Botnet**
   - Class designed to model an attacking network, with infected machines inside the attacking network that will be sending requests to a victim network. Properties handling timing and duration have been removed due to the nature of the SimPy clock, and a field storing the client objects has been added to the class. Changes to the timing and duration properties may change come DataCollector implementation.
5. **LegitimateTrafficNetwork**
   - Class designed to model a legitimate network of machines, with legitimate machines inside the network that will send requests to the same target network at a reasonable rate. Properties handling timing and duration have been removed due to the nature of the SimPy clock, and a field storing the client objects has been added to the class. Changes to the timing and duration properties may change come DataCollector implementation.
6. **Network**
   - Class designed to model a network of servers. Class is extremely simliar to the UML Class Diagram provided in initial proposal with the exception of two added fields, name: str (for debugging) and request_count: int (to keep a count of how many requests hit the network).
7. **NetworkRouter**
    - Class designed to model a network router to route traffic to servers. No changes made from proposal.
8. **NetworkServer**
    - Class designed to model a network server and process requests, process delay and resource have been removed by virtue of how requests will be handled using the SimPy library.
9. **Request**
    - Class designed to model a request made to the server, all fields have been kept the same with the exception of the removal of the requestID, as the sourceID will stamp each request with a unique identifier. The functionality desired from requestID is encapsulated by keeping the count recorded on the server. 
10. **DataCollector**
    - Class designed to collect statistics about the simulation, yet to be implemented.


