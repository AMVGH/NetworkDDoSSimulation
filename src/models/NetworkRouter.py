from src.models.NetworkServer import NetworkServer
from src.models.Request import Request


class NetworkRouter:
    def __init__(self, authorized_servers: list[NetworkServer]):
        self.authorized_servers = authorized_servers

    #TODO: Implement adaptive routing algorithm and load balancing for traffic
    def route_request(self, request: Request):
        #Zero latency assumption as outlined in the proposal; so analyze server load, capacity, heath, errors, utilization
        server = self.authorized_servers[0]
        server.receive_request(request)

