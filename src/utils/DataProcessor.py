# TODO: Data Calculations based on the config and algorithms -- any extrapolations on data like throughput calculations, or any additional logic goes here
# - Validation approaches against real-world DDoS patterns ^
from src.utils.DataCollector import DataCollector


# TODO: Implement to Calculate Expected vs. Actual
# - Probability of Depletion of Bandwidth Exhaustion
# - Probability of Depletion of Victim Resources
# - Probability of Successful Attack

#TODO: Check the other modules and refine the data being collected and plotted, update the plotting module and metric display
# - Metrics to Display:
#       - Server Response times
#      X - Ability to serve legitimate network traffic (throughput)
#      X - Performance degradation under load
#      X - Legitimate request drop rate
#       - Request Response time
#      X - Queue length
#      X - Queue Utilization
#      X - CPU Utilization
#       Response Metrics from Feedback:
#       - Request Generation Rate vs. Served Rate over time
#       - Drop Rate Patterns
#       - Legitimate vs Malicious Traffic Impact

class DataProcessor:
    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector

