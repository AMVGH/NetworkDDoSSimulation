# Network DDoS Simulation

**Author:** Alex Valentin

**Course:** CS 4632 Section W01

## Project Overview
The aim of this project is to analyze the impact of malicious network traffic on network systems. This area of study is extremely relevant to the overall network system domain, especially considering the rise of DDoS attacks against large enterprise services year-over-year. The results intend to explore how Distributed Denial of Service attacks (DDoS) impact server response time and the ability to serve legitimate network traffic, furthermore, how do safeguards such as load-balancing help reduce latency, improve throughput, and prevent server deterioration when under attack. This project will simulate legitimate and malicious network traffic, servers and server responses, and network performance degradation under load. Items outside the scope of this project and thus will not be included in the final simulation include the implementation of End-to-End security protocols (i.e.: TLS handshakes, firewalls, IDS/IPS).

## Installation Instructions and Usage Guide
### Installing Dependencies
Ensure that **Python Version 3.x** is installed on your local machine and have the required packages installed:

```bash
pip install simpy matplotlib pytest
```

Dependency versions can be found in [requirements.txt](requirements.txt)

### Running the Simulation
In order to run the simulation clone the repository to your local environment and make sure all necessary dependencies are installed. After this, simply update the simulation configuration variables found in [config.py](src/config.py), once the configuration is set to your liking simply navigate to [main.py](src/main.py) and run the simulation.

## Project Status
The current implementation of the malicious network traffic simulation includes all core models and algorithms outlined in the initial proposal, and delivers all the expected functionality that was necessary to capture the system dynamics described in M1. Users can configure the simulation parameters via the provided configuration file and receive detailed, comprehensive data surrounding simulation outcomes. The implementation supports the following key features: **a)** Legitimate and Malicious Network Request Generation, **b)** Modified Adaptive Routing to Facilitate Network Routing Decisions, **c)** Bandwidth Exhaustion, Depletion of Resources, and Successful Attack Probability Tooling, **d)** Modified Centralized C&C Topology for Issuing Malicious Client Instructions, **e)** FIFO Network Server Request Processing Logic, **f)** Comprehensive Data Collection and Management Tooling, **g)** Network Representation Proportional to Real-World Enterprise Network Surface Area and Processing Capability, **h)** Live Simulation Logging with State Data, **i)** Data Visualization and Exporting Tooling, **j)** Server Shutdown Mechanisms, and **k)** Comprehensive Calculation Tooling for Payloads and Simulation Outcomes. All of the implementation supporting these key features are either supported by literature provided in the initial proposal, or are supported by additional research conducted over the course of development.

## Example Outputs
Simulation outcomes should display results in a comprehensive comma separated format similar to the following examples: https://github.com/AMVGH/NetworkRunData 

## Architecture Overview
The main components in the simulation include the following: 

1. **BaseNetworkClient**
   - **Description:** Base class that LegitimateNetworkClient and MaliciousNetworkClient derive from, the class successfully captures the core functionality and behavior outlined in the initial proposal. The only deviation from the initial UML Class Diagram is the addition of traffic_type to house the type of traffic that will be sent from the client. Furthermore, the following fields have been added for client-level request tracking: requests_sent, successful_response, and no_response.
2. **LegitimateNetworkClient**
   - **Description:** Inherits everything from BaseNetworkClient, no differences exist between implementation and proposal.
3. **MaliciousNetworkClient**
   - **Description:** Inherits everything from BaseNetworkClient, isEnabled and the associated Getters and Setters have been discarded.
4. **BaseNetworkModel (NEW)**
   - **Description:** Base class that both Botnet and LegitimateTrafficNetwork derive from, at their core Botnet and LegitimateTrafficNetwork exhibit the same behavior, so there was no need to rewrite the same function multiple times in two separate classes. Properties in the base class are as follows: env, network_type, client_count, request_rate, target_network, load_size_lower, load_size_upper, and network_clients. attackStart, attackDuration, and attackProcess have been removed from the final implementation. While the base class properly captures the behavior of what was outlined for the two child classes, there was no need for these fields due to the nature of the SimPy library and how processes are managed.
5. **Botnet**
   - **Description:** Class designed to model an attacking network, with infected machines inside the attacking network that will be send requests to a predefined victim network. Botnet inherits everything from the parent BaseNetworkModel class.
6. **LegitimateTrafficNetwork**
   - **Description:** Class designed to model a network of interconnected, uninfected machines. Legitimate machines inside the network will send requests to a predefined target network at a fixed rate. LegitimateTrafficNetwork inherits everything from the parent BaseNetworkModel class.
7. **Network**
   - **Description:** Class designed to model a network of servers. Class is extremely similar to the UML Class Diagram provided in initial proposal except two added fields, dropped_no_server_available and incoming_request_count. These fields were added in order to keep a count of how many requests hit the network and how many requests are dropped from the network. This was done in order to resolve issues with duplicate request_ids, as when the request_id was generated by the client there was the issue of having duplicate Request IDs (RequestID: 1, 2, 3, ...) with different origins. Now the network "stamps" each request_id with the number in incoming_request_count in order to resolve any issues with conflicting ids. Furthermore, the dropped_no_server_available field was added to the Network to better model how real world networks track dropped requests and to avoid confusion when assessing the simulation results. Now, as opposed to seeing 30,000 dropped requests each from 10 different servers during an outage (in a simulation run with only 60,000 requests total), the dropped requests no longer propagate through all the offline servers, and instead we have one value for if a request is dropped from a server/servers being offline. This better captures what actually occurred during the simulation run.
8. **NetworkRouter**
    - **Description:** Class designed to model a network router to route traffic to servers. No changes made from proposal besides the removal of the currentAlgorithm field. Since only one refined algorithm for request routing will be implemented, there was no need to keep this field included in the class.
9. **NetworkServer**
    - **Description:** Class designed to model a network server and process requests, process delay has been removed by virtue of how requests will be handled using the SimPy library using timeouts according to the request load size and server utilization. The resourceCapacity field has been changed to processing_power to better capture its usage in the context of the simulation. Many fields for collecting server metrics and driving simulation logic have been added in order to help facilitate data collection and to make the simulation more accurate and robust. These fields include: max_requests_concurrent, max_request_queue_len, cpu_utilization, process_queue_utilization, server_health, time_spent_offline, is_server_online, increased_utilization, high_utilization, critical_utilization, request_process_worker, request_queue, total_requests_received, total_requests_processed, dropped_request_queue_full, dropped_requests_timeout, and dropped_requests_high_load.
10. **Request**
    - **Description:** Class designed to represent a request sent to the target network. The class still maintains fields outlined in the proposal such as source_id, traffic_type, load_size, arrival_time, and served_time. As stated previously, request_id was removed from the request class due to a bug with duplicate IDs. Additional fields have been added to the class to help support simulation functionality such as: is_served, is_routed, seen_by, and an on_completion callback.
11. **DataHandler (Renamed from DataCollector)**
    - **Description:** Class designed to be an all encompassing body for data collection, calculation, manipulation, and exporting, as opposed to the single collection device outlined in M1. The class attributes captures all the behavior outlined by the attributes in M1, and expands the functionality of the class substantially by allocating functionality for collecting time-series metrics, data calculation, data manipulation, and exporting. Many class attributes have been added in order to achieve the final implementation. 
12. **SimulationExecutive**
    - **Description:** Class designed to house all the entities of the simulation and run the simulation. The implementation remains almost identical to the implementation outlined in the proposal, with the only deviation being simulationDuration being one of the parameters now included in [config.py](src/config.py).
13. **ConfigValidator (NEW)**
    - **Description:** Validates the parameters provided in [config.py](src/config.py) to ensure that all user-configured parameters are reasonable and will not cause errors.
14. **GenericEnums (NEW)**
    - **Description:** Houses miscellaneous values such as non-configurable weights and ranges in order to reduce the presence of 'magic' numbers throughout the solution and make the simulation more robust. 
15. **DataPlotter (NEW)**
    - **Description:** Houses all data visualization mechanisms and build graphics concerning simulation outcome metrics.
16. **ProbabilityEngine (NEW)**
    - **Description:** Implements the probability algorithms and relevant calculations for Probability of Depletion of Bandwidth, Probability of Depletion of Victim Resources, and Probability of Successful Attack.
17. **TestingEngine (NEW)**
    - **Description:** Houses all relevant testing functionality.
