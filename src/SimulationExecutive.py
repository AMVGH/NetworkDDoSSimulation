import simpy
from src.models.Network import Network
from src.models.Botnet import Botnet
from src.models.LegitimateTrafficNetwork import LegitimateTrafficNetwork
from src.utils.DataCollector import DataCollector
from src.utils.DataPlotter import DataPlotter
from src.utils.GenericEnums import TRAFFICTYPES
from config import *

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
            MALICIOUS_LOAD_SIZE_LOWER,
            MALICIOUS_LOAD_SIZE_UPPER
        )
        self.legitimate_network = LegitimateTrafficNetwork(
            self.env,
            TRAFFICTYPES.LEGITIMATE.value,
            LEGITIMATE_CLIENT_COUNT,
            LEGITIMATE_TRAFFIC_RATE,
            self.target_network,
            LEGITIMATE_LOAD_SIZE_LOWER,
            LEGITIMATE_LOAD_SIZE_UPPER
        )
        self.data_collector = DataCollector(env=self.env,
                                            target_network=self.target_network,
                                            botnet=self.botnet,
                                            legitimate_traffic_network=self.legitimate_network)

    def run_simulation(self):
        #Runs the data collection process prior to starting traffic to get entire simulation snapshot
        self.data_collector.start_data_collection()

        #Runs processes to generate requests and hit the target network
        self.botnet.start_traffic()
        self.legitimate_network.start_traffic()
        self.env.run(until=SIMULATION_DURATION)

        #Data Collection and Simulation Cleanup
        self.data_collector.cleanup_remaining_requests()
        self.data_collector.print_metrics_at_intervals(interval=INTERVAL_OUTPUT_POLLING)
        self.data_collector.print_simulation_outcomes()

        #Passes data_collector context to the data_visualizer
        data_visualizer = DataPlotter(self.data_collector)
        data_visualizer.visualize_all_results()

