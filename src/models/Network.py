import simpy
from src.models.NetworkRouter import NetworkRouter
from src.models.NetworkServer import NetworkServer

class Network:
    def __init__(self, env: simpy.Environment):
        self.env = env