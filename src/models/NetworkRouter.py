from src.models.NetworkServer import NetworkServer
from src.models.Request import Request


class NetworkRouter:
    def __init__(self, authorized_servers: list[NetworkServer]):
        self.authorized_servers = authorized_servers

    #TODO: Load Balancing Approach Done: Research Potential for Adaptive Routing by Adding Additional Params, however there is no network topology weights and zero latency assumption as outlined in the proposal
    def route_request(self, request: Request):
        # Load balancing using server_health, an extrapolation of CPU utilization and Queue Utilization
        # (Demonstrating server load, capacity, health, and utilization analysis - POTENTIAL for accounting drops in future)

        online_servers = [server for server in self.authorized_servers if server.is_server_online]
        if not online_servers:
            return False
        else:
            #See about additional load balancing params
            target_server = min(online_servers, key=lambda server: server.server_health)
            target_server.receive_request(request)
            return True

