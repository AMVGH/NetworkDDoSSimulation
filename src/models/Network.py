import simpy
from src.models.Request import Request
from src.models.NetworkRouter import NetworkRouter
from src.models.NetworkServer import NetworkServer
from src.config import NUM_SERVERS

class Network:
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.name = "KSU Network"
        self.request_count = 0
        self.network_servers = [NetworkServer(
            self.env,
            f"NetworkServer{i}",
            100
        ) for i in range(NUM_SERVERS)]
        self.network_router = NetworkRouter(self.network_servers)

    #TODO: Implement server routing, at the moment just prints that requests have arrived as a P.O.C
    def process_request(self, request: Request):
        self.request_count += 1
        print(f"Network ({self.name}) has received request ID: {self.request_count}, Source: {request.source_id}, TrafficType: {request.traffic_type}, LoadSize: {request.load_size}, at {self.env.now}")