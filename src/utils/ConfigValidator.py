import src.config as config
from src.config import *


def validate_config():
    if SIMULATION_DURATION < 60 or SIMULATION_DURATION > 1800:
        print("[ERROR] SIMULATION_DURATION must be between 60 and 1800")
        return False
    elif NUM_SERVERS < 5 or NUM_SERVERS > 50:
        print("[ERROR] NUM_SERVERS must be between 5 and 50")
        return False
    elif REQUEST_TIMEOUT < 5 or REQUEST_TIMEOUT > 30:
        print("[ERROR] REQUEST_TIMEOUT must be between 5 and 30")
        return False
    elif SERVER_TIMEOUT < 1 or SERVER_TIMEOUT > 10:
        print("[ERROR] SERVER_TIMEOUT must be between 1 and 10")
        return False
    elif PROCESSING_POWER < 100 or PROCESSING_POWER > 500:
        print("[ERROR] PROCESSING_POWER must be between 100 and 500")
        return False
    elif MAX_REQUESTS_CONCURRENT < 10 or MAX_REQUESTS_CONCURRENT > 50:
        print("[ERROR] MAX_REQUESTS_CONCURRENT must be between 10 and 50")
        return False
    elif MAX_REQUEST_QUEUE_LENGTH < 100 or MAX_REQUEST_QUEUE_LENGTH > 1000:
        print("[ERROR] MAX_REQUEST_QUEUE_LENGTH must be between 100 and 1000")
        return False
    elif LEGITIMATE_TRAFFIC_RATE < 1 or LEGITIMATE_TRAFFIC_RATE > 5:
        print("[ERROR] LEGITIMATE_TRAFFIC_RATE must be between 1 and 5")
        return False
    elif LEGITIMATE_CLIENT_COUNT < 100 or LEGITIMATE_CLIENT_COUNT > 2000:
        print("[ERROR] LEGITIMATE_CLIENT_COUNT must be between 100 and 2000")
        return False
    elif MALICIOUS_TRAFFIC_RATE < 10 or MALICIOUS_TRAFFIC_RATE > 50:
        print("[ERROR] MALICIOUS_TRAFFIC_RATE must be between 10 and 50")
        return False
    elif MALICIOUS_CLIENT_COUNT < 50 or MALICIOUS_CLIENT_COUNT > 500:
        print("[ERROR] MALICIOUS_CLIENT_COUNT must be between 50 and 500")
        return False

    weight_sum = CPU_UTILIZATION_HEALTH_WEIGHT + QUEUE_UTILIZATION_HEALTH_WEIGHT
    if abs(weight_sum - 1.0) > 0.001:
        print(f"[ERROR] CPU and Queue Utilization weights must total 1.0 (Current: {weight_sum})")
        return False

    avg_malicious = (MALICIOUS_LOAD_SIZE_LOWER + MALICIOUS_LOAD_SIZE_UPPER) / 2
    avg_legitimate = (LEGITIMATE_LOAD_SIZE_LOWER + LEGITIMATE_LOAD_SIZE_UPPER) / 2
    if avg_malicious <= avg_legitimate:
        print(f"[ERROR] Average malicious load must be greater than average legitimate load")
        return False

    # Validate utilization thresholds are in correct order and boundaries
    if not (0.70 <= INCREASED_UTILIZATION <= 0.80):
        print("[ERROR] INCREASED_UTILIZATION must be between 0.70 and 0.80")
        return False
    elif not (0.81 <= HIGH_UTILIZATION <= 0.90):
        print("[ERROR] HIGH_UTILIZATION must be between 0.81 and 0.90")
        return False
    elif not (0.91 <= CRITICAL_UTILIZATION <= 1.0):
        print("[ERROR] CRITICAL_UTILIZATION must be between 0.91 and 1.0")
        return False
    elif not (INCREASED_UTILIZATION < HIGH_UTILIZATION < CRITICAL_UTILIZATION):
        print("[ERROR] Utilization thresholds must be: INCREASED < HIGH < CRITICAL")
        return False

    # Validate other float parameters
    if not (0.0 <= CPU_UTILIZATION_HEALTH_WEIGHT <= 1.0):
        print("[ERROR] CPU_UTILIZATION_HEALTH_WEIGHT must be between 0.0 and 1.0")
        return False
    elif not (0.0 <= QUEUE_UTILIZATION_HEALTH_WEIGHT <= 1.0):
        print("[ERROR] QUEUE_UTILIZATION_HEALTH_WEIGHT must be between 0.0 and 1.0")
        return False
    elif not (0.0 <= OFFLINE_CLEAR_THRESHOLD <= 1.0):
        print("[ERROR] OFFLINE_CLEAR_THRESHOLD must be between 0.0 and 1.0")
        return False
    elif not (0.0 <= HIGH_UTILIZATION_REJECTION_RATE <= 1.0):
        print("[ERROR] HIGH_UTILIZATION_REJECTION_RATE must be between 0.0 and 1.0")
        return False

    return True