#Build initial data collection mechanisms
from src.models.Botnet import Botnet
from src.models.LegitimateTrafficNetwork import LegitimateTrafficNetwork
from src.models.Network import Network


class DataCollector:
    def __init__(self, target_network: Network, botnet: Botnet, legitimate_traffic_network: LegitimateTrafficNetwork):
        self.target_network = target_network
        self.botnet = botnet
        self.legitimate_traffic_network = legitimate_traffic_network

        #Simulation Metrics
        self.total_generated_requests = 0
        self.total_requests_accounted_for = 0
        self.total_requests_served = 0
        self.total_requests_dropped_queue_full = 0
        self.total_requests_dropped_timeout = 0
        self.total_requests_dropped_network_down = 0


    def print_simulation_outcomes(self):
        for server in self.target_network.network_servers:
            print()
            print(f"=========== SIMULATION OUTCOMES [Server {server.server_id}] ==========")
            print(f"Served Requests: {server.total_requests_processed}")
            print(f"Dropped Requests Queue Full: {server.dropped_requests_queue_full}")
            print(f"Dropped Requests Process Timeout: {server.dropped_requests_timeout}")

        print()
        print("=========== FINAL SIMULATION OUTCOMES ==========")
        print(f"Total Requests Generated: {self.total_generated_requests}")
        print(f"Total Served Requests: {self.total_requests_served}")
        print(f"Total Drops (Queue Full): {self.total_requests_dropped_queue_full}")
        print(f"Total Drops (Timeout): {self.total_requests_dropped_timeout}")
        print(f"Total Drops (No Server Available): {self.total_requests_dropped_network_down}")
        print(f"All Requests Accounted For: {self.total_requests_accounted_for == self.total_generated_requests}")


    def cleanup_remaining_requests(self):
        """
        Cleans up any remaining requests that were still in the simulation pipeline at the end of the simulation.
        (i.e.: If 50,000 requests are generated in X timeframe, but at the end of X 5,000 are still in pipeline, results will not properly
        capture the full simulation snapshot due to data being cutoff)
        """
        for server in self.target_network.network_servers:
            #Counts the remaining request as timeout requests as they could not be processed in the simulation timeframe
            remaining_in_queue = len(server.request_queue.items)
            server.dropped_requests_timeout += remaining_in_queue

            #Counts any requests that were being processed by a worker process as processed requests as it
            # would've been marked served if had not been cut off by simulation timeframe
            in_progress = server.request_process_worker.count
            server.total_requests_processed += in_progress

            #Adds up simulation totals
            self.total_requests_served += server.total_requests_processed
            self.total_requests_dropped_queue_full += server.dropped_requests_queue_full
            self.total_requests_dropped_timeout += server.dropped_requests_timeout

        # Include network-wide drops (requests rejected because no servers online)
        self.total_requests_dropped_network_down = self.target_network.dropped_no_server_available

        self.total_generated_requests = self.target_network.incoming_request_count
        self.total_requests_accounted_for = self.total_requests_served + self.total_requests_dropped_queue_full + self.total_requests_dropped_timeout + self.total_requests_dropped_network_down