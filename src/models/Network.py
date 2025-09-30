import simpy
from src.models.Request import Request
from src.models.NetworkRouter import NetworkRouter
from src.models.NetworkServer import NetworkServer
from src.config import PROCESSING_POWER, MAX_REQUESTS_CONCURRENT, MAX_REQUEST_QUEUE_LENGTH, NUM_SERVERS

class Network:
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.network_servers = [NetworkServer(
            self.env,
            f"NetworkServer{i}",
            PROCESSING_POWER,
            MAX_REQUESTS_CONCURRENT,
            MAX_REQUEST_QUEUE_LENGTH,
        ) for i in range(NUM_SERVERS)]
        self.network_router = NetworkRouter(self.network_servers)
        self.incoming_request_count = 0
        self.dropped_no_server_available = 0

    def process_request(self, request: Request):
        self.incoming_request_count += 1
        request.set_request_id(self.incoming_request_count)
        accepted = self.network_router.route_request(request)
        if not accepted:
            self.dropped_no_server_available += 1