import simpy
from src.models.Network import Network
from src.models.LegitimateNetworkClient import LegitimateNetworkClient


class LegitimateTrafficNetwork:
   def __init__(self, env: simpy.Environment, traffic_rate: float, legitimate_client_count: int, target_network: Network):
      self.env = env
      self.traffic_rate = traffic_rate
      self.legitimate_client_count = legitimate_client_count
      self.target_network = target_network
      self.clients = []

      for i in range(self.legitimate_client_count):
         legitimate_client = LegitimateNetworkClient(
            self.env,
            self.target_network,
            f"LegitimateNetworkClient{i}",
            self.traffic_rate
         )
         self.clients.append(legitimate_client)

