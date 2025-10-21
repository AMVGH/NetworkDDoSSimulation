"""
Network DDoS Simulation Parameter Configuration

The aim of this simulation is to analyze the impact of malicious network traffic on network systems. This
area of study is extremely relevant to the overall network system domain, especially considering the rise of DDoS
attacks against large enterprise services year-over-year. The results intend to explore how Distributed Denial of
Service attacks (DDoS) impact server response time and the ability to serve legitimate network traffic, furthermore, how
do safeguards such as load-balancing help reduce latency, improve throughput, and prevent server deterioration when under
attack. This project will simulate legitimate and malicious network traffic, servers and server responses, and network
performance degradation under load.

The configuration parameters are based on research gathered from the following:
        [1] - (Cloudflare) DDoS Threat Report for 2025 Q1
            URL: https://radar.cloudflare.com/reports/ddos-2025-q1
        [2] - (Cloudflare) DDoS Threat Report for 2025 Q2
            URL: https://radar.cloudflare.com/reports/ddos-2025-q2#id-29-attack-size-duration
        [3] - (Cloudflare) DDoS Threat Report for 2024 Q4
            URL: https://radar.cloudflare.com/reports/ddos-2024-q4#id-16-attack-size
        [4] - (Cloudflare) Load Balancing Monitor Groups: Multi-Service Health Checks for Resilient Applications
            URL: https://blog.cloudflare.com/load-balancing-monitor-groups-multi-service-health-checks-for-resilient/
        [5] - (Microsoft) Distinguishing Attacks from Legitimate Traffic at an Authentication Server
            URL: https://www.microsoft.com/en-us/research/wp-content/uploads/2018/06/distinguishingBotsFromLegit.pdf?msockid=3b23323902456cee0ad42445036c6da1
        [6] - (LabEx) What Are Threshold Values for CPU, Memory, and Disk Usage?
            URL: https://labex.io/questions/what-are-threshold-values-for-cpu-memory-and-disk-usage-569502
        [7] - (Downtime Monkey) When Is A Website Considered Down ...As Opposed to Just Slow?
            URL: https://downtimemonkey.com/blog/when-is-website-down-rather-than-slow.php
        [8] - (OpenBenchmarking.org) NGINX
            URL: https://openbenchmarking.org/test/pts/nginx
        [9] - (Wikipedia Grafana) Grafana
            URL: https://grafana.wikimedia.org/d/O_OXJyTVk/home-w-wiki-status?orgId=1&from=now-24h&to=now&timezone=utc&refresh=5m
        [10] - (OneChassis) How Many Servers Are in a Data Center? Exploring Hyperscale & AWS/Google Data
            URL: https://gpuservercase.com/blog/how-many-servers-are-in-a-data-center/
        [11] - (Learn G2) 45+ DDoS Attack Statistics: Key Data and Takeaways for 2025
            URL: https://learn.g2.com/ddos-attack-statistics
        [12] - (ODown) API Response Time Standards: What's Good, Bad, and Unacceptable
            URL: https://odown.com/blog/api-response-time-standards/
        [13] - (NETSCOUT) Botnets Multiply and Level Up
            URL: https://www.netscout.com/threatreport/1h2022/wp-content/uploads/2022/09/SEC04_BOTNETS.pdf
"""

# Simulation Parameters
SIMULATION_DURATION = 120
"""
Total simulation duration in simulated seconds.
    Data Type: Integer
    Parameter Range: 60 - 1800
    Justification: Models DDoS attack durations from one simulated minute to a simulated half-hour.
"""

INTERVAL_OUTPUT_POLLING = 30
"""
Allows the user to adjust the interval that displays time series metrics in the console.
    Data Type: Integer
"""

# Network Server Parameters
NUM_SERVERS = 10
"""
The total number of servers in the simulated target network. 
    Data Type: Integer
    Parameter Range: 5 - 50
    Justification: Represents a moderately sized network service deployment. DDoS attacks
    typically target specific service clusters rather than entire infrastructures [1]. This is 
    scaled down roughly 10x from enterprise network cluster sizes in order to avoid memory issues
    and unexpected behaviors arising from host machine specifications.  
"""

REQUEST_TIMEOUT = 10
"""
The simulation duration in simulated seconds that must elapse before a request is dropped.
    Data Type: Integer
    Parameter Range: 5 - 30
    Justification: Based on user abandonment thresholds [7] and API response time
    standards [12], as well as backend response time polling from the reading outlined in the 
    research material. 
"""

SERVER_TIMEOUT = 2
"""
The simulation duration in simulated seconds that must elapse before a network server comes back online.
    Data Type: Integer
    Parameter Range: 1 - 10
    Justification: Models fast health check intervals used by load balancers [4]
    for rapid failure detection and recovery.
"""

PROCESSING_POWER = 200
"""
The number of requests per second that a server can process under normal conditions.
    Data Type: Integer
    Parameter Range: 100 - 500
    Justification: Scaled from NGINX benchmarks [8] to represent a medium-capacity
    web server while maintaining simulation performance.
"""

MAX_REQUESTS_CONCURRENT = 20
"""
The maximum number of concurrent requests that a server can process.
    Data Type: Integer
    Parameter Range: 10 - 50
    Justification: Based on web server thread pool configurations [8]. Maintains
    realistic concurrency limits for request processing.
"""

MAX_REQUEST_QUEUE_LENGTH = 500
"""
The maximum number of requests that can be in a server process queue at any given moment.
    Data Type: Integer
    Parameter Range: 100 - 1000
    Justification: Represents typical web server backlog settings [8]. Provides
    buffer for traffic bursts while preventing memory exhaustion.
"""

# Health and Utilization Parameters
CPU_UTILIZATION_HEALTH_WEIGHT = 0.4
"""
Weights for server health calculation.
    Data Type: Float
    Parameter Range: (0.0 - 1.0) 
    Justification: This metric is user configurable. If the user wishes to have the server health criteria be more reliant on 
    the CPU utilization and processing power, this metric can be updated to reflect that.
"""

QUEUE_UTILIZATION_HEALTH_WEIGHT = 0.6
"""
Weights for server health calculation.
    Data Type: Float
    Parameter Range: (0.0 - 1.0) 
    Justification: This metric is user configurable. If the user wishes to have the server health criteria be more reliant on 
    the QUEUE utilization and number of incoming network traffic, this metric can be updated to reflect that.
"""

OFFLINE_CLEAR_THRESHOLD = 0.6
"""
The queue utilization that must be hit in order for the server to come back online.
    Data Type: Float
    Parameter Range: (0.0 - 1.0) 
    Justification: This metric is user configurable. The user is able to configure this metric to have the server come on 
    at different thresholds of queue utilization.
"""

HIGH_UTILIZATION_REJECTION_RATE = 0.2
"""
The amount of incoming requests that should be rejected if the CPU utilization is high.
    Data Type: Float
    Parameter Range: 0.0 - 1.0
    Justification: This metric is user configurable. The user is able to configure this metric to have the server reject 
    a certain percent of incoming requests if the CPU utilization is high.
"""

INCREASED_UTILIZATION = 0.70
"""
The threshold in which the CPU is considered to be under increased load.
    Data Type: Float
    Parameter Range: (.70 - .80)
    Justification: [6] Based on the article, typical increased CPU usage is within this threshold.
"""

HIGH_UTILIZATION = 0.85
"""
The threshold in which the CPU is considered to be under high load.
    Data Type: Float
    Parameter Range: (.81 - .90)
    Justification: [6] Based on the article, typical high CPU usage is within this threshold.
"""

CRITICAL_UTILIZATION = 0.95
"""
The threshold in which the CPU is considered to be under critical load.
    Data Type: Float
    Parameter Range: (.91 - 1.0)
    Justification: [6] Based on the article, typical critical CPU usage is within this threshold.
"""

# Legitimate Network Parameters
LEGITIMATE_TRAFFIC_RATE = 2
"""
The number of legitimate requests being generated by each legitimate client second.
    Data Type: Integer
    Parameter Range: 1 - 5
    Justification: Represents typical user interaction rates for web applications [12].
    Higher rates model API-heavy applications.
"""

LEGITIMATE_CLIENT_COUNT = 500
"""
Total number of legitimate clients accessing the service.
    Data Type: Integer
    Parameter Range: 100 - 2000
    Justification: Models a medium-traffic web service. Scaled to simulate
    different traffic conditions while maintaining simulation performance.
"""

LEGITIMATE_LOAD_SIZE_LOWER = 1
LEGITIMATE_LOAD_SIZE_UPPER = 3
"""
The load size boundaries for a legitimate load.
    Data Type: Integer
    Parameter Range: 1-2 (lower), 2-5 (upper)
    Justification: Represents lightweight to moderate API calls typical of
    normal user interactions [12].
"""

# Malicious Network Parameters
MALICIOUS_TRAFFIC_RATE = 20
"""
The number of malicious requests being generated by each bot per second.
    Data Type: Integer
    Parameter Range: 10 - 50
    Justification: DDoS bots generate 5-25x more traffic than legitimate users [1].
    This creates realistic attack intensity while maintaining simulation stability.
"""

MALICIOUS_CLIENT_COUNT = 100
"""
Total number of infected clients in the DDoS botnet.
    Data Type: Integer
    Parameter Range: 50 - 500
    Justification: Models small to medium botnets capable of generating
    significant DDoS pressure [1] without overwhelming the simulation.
"""

MALICIOUS_LOAD_SIZE_LOWER = 10
MALICIOUS_LOAD_SIZE_UPPER = 25
"""
The load size boundaries for a malicious load.
    Data Type: Integer
    Parameter Range: 8-15 (lower), 15-40 (upper)
    Justification: Attackers target resource-intensive endpoints, extensive database queries, 
    and heavy workloads.
"""