import math
from typing import Dict, Any, List
from dataclasses import dataclass
from src.config import *
from src.utils.GenericEnums import PROBABILITYENUMS, MEMORYENUMS

"""
Engine class designed to implement the algorithms for the following probabilities:
    - Probability of Depletion of Bandwidth Exhaustion
    - Probability of Depletion of Victim Resources 
    - Probability of Successful Attack
The engine will utilize values outlined in the config in conjunction with the formulas 
outlined in the initial proposal to create a comparative baseline for what behavior
the simulation should be exhibiting at a given time vs. what is currently being displayed.
"""

"""
Data class for storing the relevant metrics
"""
@dataclass
class ProbabilityMetrics:
    bandwidth_exhaustion_prob: float
    victim_resource_depletion_prob: float
    successful_attack_prob: float
    timestamp: float

class ProbabilityEngine:
    def __init__(self):
        self.historical_probabilities: List[ProbabilityMetrics] = []
        self.initialize_parameters()

    def initialize_parameters(self):
        self.total_processing_capacity = PROCESSING_POWER * NUM_SERVERS
        self.total_concurrent_capacity = MAX_REQUESTS_CONCURRENT * NUM_SERVERS
        self.max_queue_capacity = MAX_REQUEST_QUEUE_LENGTH * NUM_SERVERS
        self.capacity_threshold = int(self.total_processing_capacity * 0.8)
        self.max_system_capacity = min(
            self.total_concurrent_capacity + self.max_queue_capacity, 1000
        )
        self.increased_util_threshold = INCREASED_UTILIZATION
        self.high_util_threshold = HIGH_UTILIZATION
        self.critical_util_threshold = CRITICAL_UTILIZATION

    """
    Calculates the probability of bandwidth exhaustion using the formula outlined in the proposal
    """
    def calculate_bandwidth_exhaustion_probability(self, current_attack_rate: float,
                                                   legitimate_success_rate: float):
        try:
            a = current_attack_rate
            c = self.capacity_threshold
            e = self.max_system_capacity

            if a <= 0:
                return 0.0
            if c <= 0:
                return 1.0

            numerator = math.pow(a, c)
            denominator = 0.0

            for i in range(0, e + 1):
                power_term = math.pow(a, i) if i > 0 else 1.0
                factorial_term = math.factorial(i) if i > 0 else 1.0
                term = power_term / factorial_term
                denominator += term

                if term < 1e-15 and i > c:
                    break

            if denominator == 0:
                return 1.0 if a > 0 else 0.0

            probability = numerator / denominator

            if legitimate_success_rate > 0.2:
                probability *= 0.8

            return max(0.0, min(1.0, probability))

        except (ValueError, ZeroDivisionError, OverflowError):
            capacity_ratio = current_attack_rate / self.total_processing_capacity
            return min(1.0, max(0.0, capacity_ratio))

    """
    Calculates the probability of memory exhaustion - necessary for calculating victim resource depletion
    """
    def calculate_memory_exhaustion_probability(self, current_memory_utilization: float):
        if current_memory_utilization >= self.critical_util_threshold:
            return (MEMORYENUMS.CRITICAL_BASE.value +
                    (current_memory_utilization - self.critical_util_threshold) *
                    MEMORYENUMS.CRITICAL_SLOPE.value)
        elif current_memory_utilization >= self.high_util_threshold:
            base_prob = MEMORYENUMS.HIGH_BASE.value
            progress = (current_memory_utilization - self.high_util_threshold) / (
                    self.critical_util_threshold - self.high_util_threshold)
            return base_prob + progress * MEMORYENUMS.HIGH_PROGRESS.value
        elif current_memory_utilization >= self.increased_util_threshold:
            base_prob = MEMORYENUMS.INCREASED_BASE.value
            progress = (current_memory_utilization - self.increased_util_threshold) / (
                    self.high_util_threshold - self.increased_util_threshold)
            return base_prob + progress * MEMORYENUMS.INCREASED_PROGRESS.value
        else:
            return max(0.0, current_memory_utilization * MEMORYENUMS.NORMAL_MULTIPLIER.value)

    """
    Calculates the probability of depletion of victim resources using the formula outlined in the proposal
    """
    def calculate_victim_resource_depletion_probability(self, P_B: float, P_M: float,
                                                        legitimate_success_rate: float):
        base_depletion = 1 - (1 - P_B) * (1 - P_M)
        service_impact = 1.0 - legitimate_success_rate
        adjusted_depletion = base_depletion * service_impact
        return min(1.0, adjusted_depletion)

    """
    Calculates the probability of a successful attack; is an extrapolation of idealized success probability under no load versus the legitimate success rate
    """
    def calculate_successful_attack_probability(self,
                                                successful_malicious_requests: int,
                                                legitimate_success_rate: float,
                                                simulation_time: float,
                                                current_server_capacity: float = None):
        if simulation_time <= 0:
            return 0.0

        C = current_server_capacity if current_server_capacity is not None else self.total_processing_capacity
        if C <= 0:
            return 1.0

        normal_success_rate = PROBABILITYENUMS.IDEALIZED_SUCCESS_NO_ATTACK.value
        service_degradation = max(0.0, (normal_success_rate - legitimate_success_rate) / normal_success_rate)

        return min(1.0, service_degradation)

    """
    Updates stored metrics for probabilities 
    """
    def update_probabilities(self,
                             simulation_state: Dict[str, Any],
                             current_time: float) -> ProbabilityMetrics:
        current_attack_rate = simulation_state.get('current_attack_rate', 0)
        memory_utilization = simulation_state.get('memory_utilization', 0)
        successful_malicious_requests = simulation_state.get('successful_malicious_requests', 0)
        current_server_capacity = simulation_state.get('current_server_capacity')
        legitimate_success_rate = simulation_state.get('legitimate_success_rate', PROBABILITYENUMS.IDEALIZED_SUCCESS_NO_ATTACK.value)

        P_B = self.calculate_bandwidth_exhaustion_probability(current_attack_rate, legitimate_success_rate)
        P_M = self.calculate_memory_exhaustion_probability(memory_utilization)
        P_TA = self.calculate_victim_resource_depletion_probability(P_B, P_M, legitimate_success_rate)
        P_WA = self.calculate_successful_attack_probability(
            successful_malicious_requests, legitimate_success_rate, current_time, current_server_capacity
        )

        metrics = ProbabilityMetrics(P_B, P_TA, P_WA, current_time)
        self.historical_probabilities.append(metrics)

        return metrics

    """
    Returns system wide capacity information
    """
    def get_system_capacity_info(self):
        return {
            'total_processing_capacity': self.total_processing_capacity,
            'total_concurrent_capacity': self.total_concurrent_capacity,
            'max_queue_capacity': self.max_queue_capacity,
            'capacity_threshold': self.capacity_threshold,
            'max_system_capacity': self.max_system_capacity
        }

    def get_historical_probabilities(self):
        return self.historical_probabilities.copy()

    def get_average_probabilities(self):
        if not self.historical_probabilities:
            return {'bandwidth_exhaustion_probability': 0.0, 'victim_resource_depletion_probability': 0.0,
                    'successful_attack_probability': 0.0}

        total_P_B = 0.0
        total_P_TA = 0.0
        total_P_WA = 0.0
        count = len(self.historical_probabilities)

        for prob in self.historical_probabilities:
            total_P_B += prob.bandwidth_exhaustion_prob
            total_P_TA += prob.victim_resource_depletion_prob
            total_P_WA += prob.successful_attack_prob

        return {
            'bandwidth_exhaustion_probability': total_P_B / count,
            'victim_resource_depletion_probability': total_P_TA / count,
            'successful_attack_probability': total_P_WA / count
        }

    """
    Gets recent data from the historical stored probabilities 
    """
    def get_probability_trend(self, window_size: int = 10):
        recent_data = self.historical_probabilities[-window_size:]
        return {
            'bandwidth_exhaustion': [p.bandwidth_exhaustion_prob for p in recent_data],
            'resource_depletion': [p.victim_resource_depletion_prob for p in recent_data],
            'successful_attack': [p.successful_attack_prob for p in recent_data],
            'timestamps': [p.timestamp for p in recent_data]
        }