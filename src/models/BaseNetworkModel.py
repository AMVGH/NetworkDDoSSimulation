import simpy
from src.models.Network import Network
from src.models.MaliciousNetworkClient import MaliciousNetworkClient
from src.models.LegitimateNetworkClient import LegitimateNetworkClient
from src.utils.GenericEnums import TRAFFICTYPES

class BaseNetworkModel:
    def __init__(self, env: simpy.Environment, network_type: str, client_count: int, request_rate: float, target_network: Network, incoming_load_size: float):
        self.env = env
        self.network_type = network_type
        self.client_count = client_count
        self.request_rate = request_rate
        self.target_network = target_network
        self.incoming_load_size = incoming_load_size
        self.network_clients = []

        #Fills the network_client list with corresponding client objects
        for i in range(self.client_count):
            if network_type==TRAFFICTYPES.MALICIOUS.value:
                malicious_client = MaliciousNetworkClient(
                    self.env,
                    TRAFFICTYPES.MALICIOUS.value,
                    self.target_network,
                    f"{TRAFFICTYPES.MALICIOUS.value} Client No. {i + 1}",
                    self.request_rate
                )
                self.network_clients.append(malicious_client)
                continue

            elif network_type==TRAFFICTYPES.LEGITIMATE.value:
                legitimate_client = LegitimateNetworkClient(
                    self.env,
                    TRAFFICTYPES.LEGITIMATE.value,
                    self.target_network,
                    f"{TRAFFICTYPES.LEGITIMATE.value} Client No. {i + 1}",
                    self.request_rate
                )
                self.network_clients.append(legitimate_client)
                continue

    def start_traffic(self):
        for client in self.network_clients:
            self.env.process(client.generate_request(
                source_id=f"{client.client_id}",
                traffic_type=f"{client.traffic_type}",
                load_size=self.incoming_load_size
            ))