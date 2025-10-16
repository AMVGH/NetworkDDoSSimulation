from src.models.NetworkServer import NetworkServer
from src.models.Request import Request


class NetworkRouter:
    def __init__(self, authorized_servers: list[NetworkServer]):
        self.authorized_servers = authorized_servers

    """
    While a Distributed Adaptive Routing algorithm was initially described in M1, there are no network topology weights and a zero latency assumption
    for server communication. Since there are no metrics outlining network communication latency, nor the "distance" by which requests will travel, I have opted 
    to simplify the routing algorithm into a single load-balancing mechanism. The load balancing mechanism utilizes server_health, an extrapolation of CPU 
    utilization and queue utilization, in order to distribute traffic evenly among network servers. The aim of this simulation is to analyze network performance 
    degradation under load. As a result, I feel as though the implementation currently provided is adequate for analyzing performance degradation without
    impacting outcomes.
    """
    def route_request(self, request: Request):
        # Pool of online servers
        online_servers = [server for server in self.authorized_servers if server.is_server_online]

        # If there is a network outage (every server offline), return False. Server offline drops are recorded at the network level since requests
        # are being distributed among a pool of online servers.
        if not online_servers:
            return False
        else:
            # The request's target server is the healthiest server of the servers included in the online pool.
            target_server = min(online_servers, key=lambda server: server.server_health)
            # Route the request to the server
            target_server.receive_request(request)
            return True

