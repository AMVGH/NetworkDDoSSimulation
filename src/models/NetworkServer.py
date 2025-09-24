import simpy

from src.models.Request import Request


class NetworkServer:
    def __init__(self, env: simpy.Environment, server_id: str, resource_capacity: int):
        self.env = env
        self.server_id = server_id
        self.resource_capacity = resource_capacity

    def process_request(self, incoming_request: Request):
        print("Processing request")