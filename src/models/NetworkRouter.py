from src.models.NetworkServer import NetworkServer

class NetworkRouter:
    def __init__(self, authorized_servers: list[NetworkServer]):
        self.authorized_servers = authorized_servers

    def send_traffic(self):
        pass
        #implement routing algorithm