from src.config import *

def validate_config():
    # Simulation Parameters
    if not (60 <= SIMULATION_DURATION <= 1800):
        print(f"[ERROR] SIMULATION_DURATION must be between 60 and 1800 (current: {SIMULATION_DURATION})")
        return False
    if INTERVAL_DATA_POLLING <= 0:
        print(f"[ERROR] INTERVAL_DATA_POLLING must be positive (current: {INTERVAL_DATA_POLLING})")
        return False
    if INTERVAL_OUTPUT_POLLING <= 0:
        print(f"[ERROR] INTERVAL_OUTPUT_POLLING must be positive (current: {INTERVAL_OUTPUT_POLLING})")
        return False

    # Network Server Parameters
    if not (5 <= NUM_SERVERS <= 50):
        print(f"[ERROR] NUM_SERVERS must be between 5 and 50 (current: {NUM_SERVERS})")
        return False
    if not (5 <= REQUEST_TIMEOUT <= 30):
        print(f"[ERROR] REQUEST_TIMEOUT must be between 5 and 30 seconds (current: {REQUEST_TIMEOUT})")
        return False
    if not (1 <= SERVER_TIMEOUT <= 10):
        print(f"[ERROR] SERVER_TIMEOUT must be between 1 and 10 seconds (current: {SERVER_TIMEOUT})")
        return False
    if not (100 <= PROCESSING_POWER <= 500):
        print(f"[ERROR] PROCESSING_POWER must be between 100 and 500 requests/second (current: {PROCESSING_POWER})")
        return False
    if not (10 <= MAX_REQUESTS_CONCURRENT <= 50):
        print(f"[ERROR] MAX_REQUESTS_CONCURRENT must be between 10 and 50 (current: {MAX_REQUESTS_CONCURRENT})")
        return False
    if not (100 <= MAX_REQUEST_QUEUE_LENGTH <= 1000):
        print(f"[ERROR] MAX_REQUEST_QUEUE_LENGTH must be between 100 and 1000 (current: {MAX_REQUEST_QUEUE_LENGTH})")
        return False

    # Health and Utilization Parameters
    weight_sum = CPU_UTILIZATION_HEALTH_WEIGHT + QUEUE_UTILIZATION_HEALTH_WEIGHT
    if abs(weight_sum - 1.0) > 0.001:
        print(f"[ERROR] CPU and Queue Utilization weights must total 1.0 (current: {weight_sum:.3f})")
        return False
    if not (0.0 <= CPU_UTILIZATION_HEALTH_WEIGHT <= 1.0):
        print(
            f"[ERROR] CPU_UTILIZATION_HEALTH_WEIGHT must be between 0.0 and 1.0 (current: {CPU_UTILIZATION_HEALTH_WEIGHT})")
        return False
    if not (0.0 <= QUEUE_UTILIZATION_HEALTH_WEIGHT <= 1.0):
        print(
            f"[ERROR] QUEUE_UTILIZATION_HEALTH_WEIGHT must be between 0.0 and 1.0 (current: {QUEUE_UTILIZATION_HEALTH_WEIGHT})")
        return False
    if not (0.0 <= OFFLINE_CLEAR_THRESHOLD <= 1.0):
        print(f"[ERROR] OFFLINE_CLEAR_THRESHOLD must be between 0.0 and 1.0 (current: {OFFLINE_CLEAR_THRESHOLD})")
        return False
    if not (0.0 <= HIGH_UTILIZATION_REJECTION_RATE <= 1.0):
        print(
            f"[ERROR] HIGH_UTILIZATION_REJECTION_RATE must be between 0.0 and 1.0 (current: {HIGH_UTILIZATION_REJECTION_RATE})")
        return False
    if not (0.70 <= INCREASED_UTILIZATION <= 0.80):
        print(f"[ERROR] INCREASED_UTILIZATION must be between 0.70 and 0.80 (current: {INCREASED_UTILIZATION})")
        return False
    if not (0.81 <= HIGH_UTILIZATION <= 0.90):
        print(f"[ERROR] HIGH_UTILIZATION must be between 0.81 and 0.90 (current: {HIGH_UTILIZATION})")
        return False
    if not (0.91 <= CRITICAL_UTILIZATION <= 1.0):
        print(f"[ERROR] CRITICAL_UTILIZATION must be between 0.91 and 1.0 (current: {CRITICAL_UTILIZATION})")
        return False
    if not (INCREASED_UTILIZATION < HIGH_UTILIZATION < CRITICAL_UTILIZATION):
        print(
            f"[ERROR] Utilization thresholds must be: INCREASED ({INCREASED_UTILIZATION}) < HIGH ({HIGH_UTILIZATION}) < CRITICAL ({CRITICAL_UTILIZATION})")
        return False

    # Legitimate Network Parameters
    if not (1 <= LEGITIMATE_TRAFFIC_RATE <= 5):
        print(
            f"[ERROR] LEGITIMATE_TRAFFIC_RATE must be between 1 and 5 requests/second (current: {LEGITIMATE_TRAFFIC_RATE})")
        return False
    if not (100 <= LEGITIMATE_CLIENT_COUNT <= 2000):
        print(f"[ERROR] LEGITIMATE_CLIENT_COUNT must be between 100 and 2000 (current: {LEGITIMATE_CLIENT_COUNT})")
        return False
    if LEGITIMATE_LOAD_SIZE_LOWER <= 0:
        print(f"[ERROR] LEGITIMATE_LOAD_SIZE_LOWER must be positive (current: {LEGITIMATE_LOAD_SIZE_LOWER})")
        return False
    if LEGITIMATE_LOAD_SIZE_UPPER <= 0:
        print(f"[ERROR] LEGITIMATE_LOAD_SIZE_UPPER must be positive (current: {LEGITIMATE_LOAD_SIZE_UPPER})")
        return False
    if LEGITIMATE_LOAD_SIZE_LOWER > LEGITIMATE_LOAD_SIZE_UPPER:
        print(
            f"[ERROR] LEGITIMATE_LOAD_SIZE_LOWER ({LEGITIMATE_LOAD_SIZE_LOWER}) cannot be greater than LEGITIMATE_LOAD_SIZE_UPPER ({LEGITIMATE_LOAD_SIZE_UPPER})")
        return False

    # Malicious Network Parameters
    if not (10 <= MALICIOUS_TRAFFIC_RATE <= 50):
        print(
            f"[ERROR] MALICIOUS_TRAFFIC_RATE must be between 10 and 50 requests/second (current: {MALICIOUS_TRAFFIC_RATE})")
        return False
    if not (50 <= MALICIOUS_CLIENT_COUNT <= 500):
        print(f"[ERROR] MALICIOUS_CLIENT_COUNT must be between 50 and 500 (current: {MALICIOUS_CLIENT_COUNT})")
        return False
    if MALICIOUS_LOAD_SIZE_LOWER <= 0:
        print(f"[ERROR] MALICIOUS_LOAD_SIZE_LOWER must be positive (current: {MALICIOUS_LOAD_SIZE_LOWER})")
        return False
    if MALICIOUS_LOAD_SIZE_UPPER <= 0:
        print(f"[ERROR] MALICIOUS_LOAD_SIZE_UPPER must be positive (current: {MALICIOUS_LOAD_SIZE_UPPER})")
        return False
    if MALICIOUS_LOAD_SIZE_LOWER > MALICIOUS_LOAD_SIZE_UPPER:
        print(
            f"[ERROR] MALICIOUS_LOAD_SIZE_LOWER ({MALICIOUS_LOAD_SIZE_LOWER}) cannot be greater than MALICIOUS_LOAD_SIZE_UPPER ({MALICIOUS_LOAD_SIZE_UPPER})")
        return False

    # Check mean loads are correct and valid
    avg_malicious_load = (MALICIOUS_LOAD_SIZE_LOWER + MALICIOUS_LOAD_SIZE_UPPER) / 2
    avg_legitimate_load = (LEGITIMATE_LOAD_SIZE_LOWER + LEGITIMATE_LOAD_SIZE_UPPER) / 2
    if avg_malicious_load <= avg_legitimate_load:
        print(
            f"[ERROR] Average malicious load ({avg_malicious_load:.1f}) must be greater than average legitimate load ({avg_legitimate_load:.1f})")
        return False

    return True