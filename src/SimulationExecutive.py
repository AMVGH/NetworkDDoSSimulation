import simpy
from src.models.Network import Network
from src.models.Botnet import Botnet
from src.models.LegitimateTrafficNetwork import LegitimateTrafficNetwork
from src.utils.GenericEnums import TRAFFICTYPES
from config import *

#TODO: Configure how the simulation is going to be run; config file to be parsed or params read from executive body
class SimulationExecutive:
    def __init__(self):
        self.env = simpy.Environment()
        self.target_network = Network(self.env)
        self.botnet = Botnet(
            self.env,
            TRAFFICTYPES.MALICIOUS.value,
            MALICIOUS_CLIENT_COUNT,
            MALICIOUS_TRAFFIC_RATE,
            self.target_network,
            MALICIOUS_LOAD_SIZE,
        )
        self.legitimate_network = LegitimateTrafficNetwork(
            self.env,
            TRAFFICTYPES.LEGITIMATE.value,
            LEGITIMATE_CLIENT_COUNT,
            LEGITIMATE_TRAFFIC_RATE,
            self.target_network,
            LEGITIMATE_LOAD_SIZE,
        )

    #TODO: Build out and expand core functionality
    def run_simulation(self):
        #Runs processes to generate requests and hit the target network
        self.botnet.start_traffic()
        self.legitimate_network.start_traffic()
        self.env.run(until=SIMULATION_DURATION)
