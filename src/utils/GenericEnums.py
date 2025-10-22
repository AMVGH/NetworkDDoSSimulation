from enum import Enum

class TRAFFICTYPES(Enum):
    MALICIOUS = "Malicious"
    LEGITIMATE = "Legitimate"

class PROCESSENUMS(Enum):
    BASE_TIME = 1.0
    INCREASED_FACTOR_INCREASED_RANGE = 2.0
    INCREASED_FACTOR_HIGH_RANGE = 3.0
    HIGH_FACTOR_HIGH_RANGE = 5.0

class VARIANCEENUMS(Enum):
    LOWERBOUND = 0.5
    UPPERBOUND = 2.0

class PROBABILITYENUMS(Enum):
    IDEALIZED_SUCCESS_NO_ATTACK = .85

class MEMORYENUMS(Enum):
    #Critical Utilization Values
    CRITICAL_BASE = 0.90
    CRITICAL_SLOPE = 0.50

    #High Utilization Values
    HIGH_BASE = 0.70
    HIGH_PROGRESS = 0.20

    #Increased Utilization Values
    INCREASED_BASE = 0.30
    INCREASED_PROGRESS = 0.40

    #Utilization is not in threshold
    NORMAL_MULTIPLIER = 0.50

