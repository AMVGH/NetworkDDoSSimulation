import simpy
import random
from src.models.Network import Network
from src.models.Request import Request

class BaseNetworkClient:
    def __init__(self, env: simpy.Environment, traffic_type: str, target_network: Network, client_id: str, request_rate: float):
        self.env = env
        self.traffic_type = traffic_type
        self.target_network = target_network
        self.client_id = client_id
        self.request_rate = request_rate

        #Metrics for request generation and responses
        self.requests_sent = 0
        self.successful_response = 0
        self.no_response = 0

    def generate_request(self, source_id: str, traffic_type: str, load_size_lower: float, load_size_upper: float):
        while True:
            yield self.env.timeout(1 / self.request_rate)
            request_load = random.uniform(load_size_lower, load_size_upper)
            request_load = round(request_load, 4)
            request = Request(
                source_id,
                traffic_type,
                request_load,
                on_completion=self.request_outcome_callback
            )
            self.requests_sent += 1

            #Send request to the Network
            if not self.target_network.process_request(request):
                #If the network is down and returns False, increment no_response
                self.no_response += 1
            else:
                pass

    def request_outcome_callback(self, request: Request, success: bool, failure_reason: str = None):
        if success:
            self.successful_response += 1  # Actually served
        else:
            self.no_response += 1  # Failed after being accepted

