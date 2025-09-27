#TODO: Research param rules to use to best model these interactions (i.e.: Avg malicious request is 4:1 and DDoS Traffic Rate should be x:y)
    # - Configure for specific parameter ranges for attack rates and server capacities

#Simulation Parameters
SIMULATION_DURATION=100
NUM_SERVERS=1

#Network Server Parameters
REQUEST_TIMEOUT=5
SERVER_TIMEOUT=10
PROCESSING_POWER=20
MAX_REQUESTS_CONCURRENT=2
MAX_REQUEST_QUEUE_LENGTH=100

#Legitimate Network Parameters
LEGITIMATE_TRAFFIC_RATE=1
LEGITIMATE_CLIENT_COUNT=5
LEGITIMATE_LOAD_SIZE_LOWER=1
LEGITIMATE_LOAD_SIZE_UPPER=2

#Malicious Network Parameters
MALICIOUS_TRAFFIC_RATE=10
MALICIOUS_CLIENT_COUNT=30
MALICIOUS_LOAD_SIZE_LOWER=10
MALICIOUS_LOAD_SIZE_UPPER=20