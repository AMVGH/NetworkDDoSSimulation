import simpy
from src.models.Network import Network
from src.models.Request import Request

class BaseNetworkClient:
    def __init__(self, env: simpy.Environment, traffic_type: str, target_network: Network, client_id: str, request_rate: float):
        self.env = env
        self.traffic_type = traffic_type
        self.target_network = target_network
        self.client_id = client_id
        self.request_rate = request_rate

    # TODO: Traffic Generation Enhancements
    # - Resolve flat rate load sizes, should not be a consistent load size and on average mean load size for MALICIOUS > LEGITIMATE

    def generate_request(self, source_id: str, traffic_type: str, load_size: float):
        while True:
            yield self.env.timeout(1 / self.request_rate)
            request = Request(
                source_id,
                traffic_type,
                load_size
            )

            #Send request to the Network
            self.target_network.process_request(request)