import simpy
from models.Network import Network
from models.Botnet import Botnet
from models.LegitimateTrafficNetwork import LegitimateTrafficNetwork


#Simulation Parameters
SIMULATION_DURATION=1000

#Legitimate Network Parameters
LEGITIMATE_TRAFFIC_RATE=1
LEGITIMATE_CLIENT_COUNT=2

#Malicious Network Parameters
MALICIOUS_TRAFFIC_RATE=2
MALICIOUS_CLIENT_COUNT=3

#TODO: Configure how the simulation is going to be run; config file to be parsed or params read from executive body
class SimulationExecutive:
    def __init__(self):
        self.env = simpy.Environment()
        self.target_network = Network(self.env)
        self.botnet = Botnet(
            self.env,
            MALICIOUS_TRAFFIC_RATE,
            MALICIOUS_CLIENT_COUNT,
            self.target_network
        )
        self.legitimate_network = LegitimateTrafficNetwork(
            self.env,
            LEGITIMATE_TRAFFIC_RATE,
            LEGITIMATE_CLIENT_COUNT,
            self.target_network
        )

#P.O.C --> Expand logic and build out core functionality
    def run_simulation(self):
        #run processes to generate requests to hit the target networks
        print('Simulation implementation TBI')
