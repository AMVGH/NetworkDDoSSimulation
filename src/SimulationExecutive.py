import simpy
from src.models.Network import Network
from src.models.Botnet import Botnet
from src.models.LegitimateTrafficNetwork import LegitimateTrafficNetwork
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

    #TODO: Build out and expand core functionality
    def run_simulation(self):
        #Runs processes to generate requests and hit the target network
        self.botnet.start_traffic()
        self.legitimate_network.start_traffic()
        self.env.run(until=SIMULATION_DURATION)
        self.cleanup_remaining_requests()

    def cleanup_remaining_requests(self):
        """
        Cleans up any remaining requests that were still in the simulation pipeline at the end of the simulation.
        (i.e.: If 50,000 requests are generated in X timeframe, but at the end of X 5,000 are still in pipeline, results will not properly
        capture the full simulation snapshot due to data being cutoff)
        """

        total_requests_served = 0
        total_requests_dropped_queue_full = 0
        total_requests_dropped_timeout = 0

        for server in self.target_network.network_servers:
            #Counts the remaining request as timeout requests as they could not be processed in the simulation timeframe
            remaining_in_queue = len(server.request_queue.items)
            server.dropped_requests_timeout += remaining_in_queue

            #Counts any requests that were being processed by a worker process as processed requests as it
            # would've been marked served if had not been cut off by simulation timeframe
            in_progress = server.current_requests_concurrent
            server.total_requests_processed += in_progress

            #Adds up simulation totals
            total_requests_served += server.total_requests_processed
            total_requests_dropped_queue_full += server.dropped_requests_queue_full
            total_requests_dropped_timeout += server.dropped_requests_timeout

        # Include network-wide drops (requests rejected because no servers online)
        total_requests_dropped_network_down = self.target_network.dropped_no_server_available

        total_generated_requests = self.target_network.incoming_request_count
        total_requests_accounted_for = total_requests_served + total_requests_dropped_queue_full + total_requests_dropped_timeout + total_requests_dropped_network_down

        for server in self.target_network.network_servers:
            server.print_simulation_outcomes()

        print()
        print("=========== FINAL SIMULATION OUTCOMES ==========")
        print(f"Total Requests Generated: {total_generated_requests}")
        print(f"Total Served Requests: {total_requests_served}")
        print(f"Total Drops (Queue Full): {total_requests_dropped_queue_full}")
        print(f"Total Drops (Timeout): {total_requests_dropped_timeout}")
        print(f"Total Drops (No Server Available): {total_requests_dropped_network_down}")
        print(f"All Requests Accounted For: {total_requests_accounted_for == total_generated_requests}")