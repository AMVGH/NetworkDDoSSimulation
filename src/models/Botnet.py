import simpy
from src.models.Network import Network
from src.models.MaliciousNetworkClient import MaliciousNetworkClient

class Botnet:
    def __init__(self, env: simpy.Environment, traffic_rate: float, malicious_client_count: int, target_network: Network):
        self.env = env
        self.traffic_rate = traffic_rate
        self.malicious_client_count = malicious_client_count
        self.target_network = target_network
        self.clients = []

        for i in range(self.malicious_client_count):
            malicious_client = MaliciousNetworkClient(
                self.env,
                self.target_network,
                f"MaliciousNetworkClient{i}",
                self.traffic_rate
            )
            self.clients.append(malicious_client)
