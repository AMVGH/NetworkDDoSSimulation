import simpy
from src.models.Network import Network

class BaseNetworkClient:
    def __init__(self, env: simpy.Environment, target_network: Network, client_id: str, request_rate: float):
        self.env = env
        self.target_network = target_network
        self.client_id = client_id
        self.request_rate = request_rate

    def generate_request(self):
        print('Generating request...')