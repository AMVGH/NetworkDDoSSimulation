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
In order to run the simulation clone the repository to your local environment and make sure all necessary dependencies are installed. After this, simply update the simulation configuration variables found in [config.py](src/config.py), once the configuration is set to your liking simply navigate to [main.py](src/main.py) and run the simulation. At the current moment, simulation outcomes will be written to the terminal.

## Project Status
At the current moment, class models and their properties have been implemented across the board with the core simulation functionality being captured. Users can now configure the simulation parameters found in [config.py](src/config.py) to their liking and get simulation results regarding the total requests generated, total served requests, and total request drops with their causes. Furthermore, the user can see a breakdown per server to see how these metrics deviate between server instances. While the core implementation logic is captured, the simulation as a whole requires further refinement in order to demonstrate the real world behaviors of a network under load as accurately as possible. Methods handling data visualization, as well as enhanced data collection and routing have yet to be implemented. Furthermore, testing logic has yet to be implemented, and there are some minor bugs concerning utilization metrics that need to be ironed out before moving forward. Overall, the initial implmentation serves as a very strong proof of concept and deviates very little from what is outlined in the original proposal.  

## Architecture Overview
The main components in the simulation include the following: 

- **BaseNetworkClient**
   - Base class that the two network clients derive from, no differences exist between what is implemented and what is proposed in the UML Class diagram besides the addition of a traffic_type field to capture the type of traffic the client object will be sending. The client objects are still designed to generate requests to send to the Network and will behave in the same fashion as outlined in the initial proposal.
  
2. **LegitimateNetworkClient**
   - Inherits everything from BaseNetworkClient, no differences exist between implementation and proposal.

3. **MaliciousNetworkClient**
   - Inherits everything from BaseNetworkClient, isEnabled and the functions to set and get the network state are not implemented at the moment and may potentially be discarded due to how processes will be handled in SimPy.
  
4 .**BaseNetworkModel (NEW)**
   - Base class that both Botnet and LegitimateTrafficNetwork derive from, at their core, Botnet and LegitimateTraffic network exhibit the same behavior, so I chose to capture this behavior in an associated base class as opposed to writing two functions that will both generate requests to hit the target network. The properties in the base class are as follows: env, network_type, client_count, request_rate, traget_network, load_size_lower, load_size_upper, and network_clients. The start, duration, and process propeties do not exist in this base class as opposed to the UML Class Diagram outlined in the initial proposal. While the base class properly captures the behavior of what was outlined for the two classes, there was no need for these fields due to the nature of the SimPy library and how processes are managed.

5. **Botnet**
   - Class designed to model an attacking network, with infected machines inside the attacking network that will be sending requests to a victim network. At the current moment Botnet inherits everything from the parent BaseNetworkModel class.

6. **LegitimateTrafficNetwork**
   - Class designed to model a legitimate network of machines, with legitimate machines inside the network that will send requests to the same target network at a reasonable rate. At the current moment LegitimateTrafficNetwork inherits everything from the parent BaseNetworkModel class.

7. **Network**
   - Class designed to model a network of servers. Class is extremely simliar to the UML Class Diagram provided in initial proposal with the exception of two added fields, dropped_no_server_available: int and incoming_request_count: int (to keep a count of how many requests hit the network and how many requests are dropped from the network). These fields were added in order to resolve issues with duplicate request_ids, as when the request_id was generated by the client there was the issue of having duplicate Request IDs (RequestID: 1, 2, 3, ...) with different origins. Now the network "stamps" each request_id with the number in incoming_request_count in order to resolve any issues with conflicting ids. Furthermore, the dropped_no_server_available field was added to the Network to better model how real world networks track dropped requests and to avoid confusion when assessing the simulation results. Now, as opposed to seeing 30,000 dropped requests each from 10 different servers during an outage (in a simulation run with only 60,000 requests total), the dropped requests no longer propagate through all of the offline servers and instead we have one value for if a request is dropped from a server/servers being offline, better capturing what actually occurred during the simulation run.

8. **NetworkRouter**
    - Class designed to model a network router to route traffic to servers. No changes made from proposal besides the removal of the currentAlgorithm field. Since only one refined algorithm for request routing will be implemented, there was no need to keep this field included in the class.

9. **NetworkServer**
    - Class designed to model a network server and process requests, process delay has been removed by virtue of how requests will be handled using the SimPy library using timeouts according to the request load size and server utilization. The resourceCapacity field has been changed to processing_power to better capture its usage in the context of the simulation. Many fields for collecting server metrics and driving simulation logic have been added in order to help facilitate data collection and to make the simulation more accurate and robust. These fields include: max_requests_concurrent, max_request_queue_len, current_requests_concurrent, cpu_utilization, process_queue_utilization, queue_length, server_health, is_server_online, increased_utilization, high_utilization, critical_utilization, total_requests_processed, dropped_request_server_offline, dropped_request_queue_full, and dropped_requests_timeout.

10. **Request**
    - Class designed to model a request made to the server, all fields have been kept the same with the addition of is_served and is_routed. The addition of these fields is to both serve as safeguards during simulation execution as well as a means for possible recording service rate in the future.

11. **DataCollector**
    - Class designed to collect statistics about the simulation, at the current momement the fields include: target_network, botnet, legitimate_traffic_network, total_generated_requests, total_requests_accounted_for, total_requests_served, total_requests_dropped_queue_full, total_requests_dropped_timeout, and total_requests_dropped_network_down. While some of these fields capture behavior outlined in the UML class diagram and have simply been renamed since the proposal, fields such as simulationStartTime and simulationEndTime will no longer be included due to the nature of the SimPy clock. There are also fields that have yet to be implemnted such as meanReqResponseTime that will be present in the final simulation but have not yet been implemented at the time of the M2 deadline.

12. **SimulationExecutive**
    - Class designed to house all of the entities of the simulation and run the simulation. The implementation remains almost identical to the implementation outlined in the proposal, with the only deviation being simulationDuration being one of the parameters now included in (config.py)[src/config.py].


