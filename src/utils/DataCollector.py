#Build initial data collection mechanisms
import simpy

from src.models.Botnet import Botnet
from src.models.LegitimateTrafficNetwork import LegitimateTrafficNetwork
from src.models.Network import Network

#TODO: Build output mechanisms for CSV, JSON, etc. --> Possibly do Data Calc --> revisit if best assert implementation

class DataCollector:
    def __init__(self, env: simpy.Environment, target_network: Network, botnet: Botnet, legitimate_traffic_network: LegitimateTrafficNetwork):
        self.env = env
        self.target_network = target_network
        self.botnet = botnet
        self.legitimate_traffic_network = legitimate_traffic_network

        #Simulation Time-Series Metrics
        self.time_series = {
            'time': [],
            'total_generated': [],
            'total_served': [],
            'total_drops_queue_full': [],
            'total_drops_timeout': [],
            'total_drops_high_load': [],
            'total_drops_no_server': []
        }

        #Simulation Total Metrics
        self.total_generated_requests = 0
        self.total_requests_accounted_for = 0
        self.total_requests_served = 0
        self.total_requests_dropped_queue_full = 0
        self.total_requests_dropped_process_timeout = 0
        self.total_requests_dropped_high_load = 0
        self.total_requests_dropped_network_down = 0

    def start_data_collection(self):
        self.env.process(self.collect_data())

    def collect_data(self):
        while True:
            current_time = self.target_network.env.now

            # Record time
            self.time_series['time'].append(current_time)

            self.time_series['total_generated'].append(self.target_network.incoming_request_count)
            self.time_series['total_served'].append(
                sum(s.total_requests_processed for s in self.target_network.network_servers))
            self.time_series['total_drops_queue_full'].append(
                sum(s.dropped_requests_queue_full for s in self.target_network.network_servers))
            self.time_series['total_drops_timeout'].append(
                sum(s.dropped_requests_process_timeout for s in self.target_network.network_servers))
            self.time_series['total_drops_high_load'].append(
                sum(s.dropped_requests_high_load for s in self.target_network.network_servers))
            self.time_series['total_drops_no_server'].append(self.target_network.dropped_no_server_available)

            yield self.target_network.env.timeout(1.0)


    def print_simulation_outcomes(self):
        for server in self.target_network.network_servers:
            print()
            print(f"=========== SIMULATION OUTCOMES [Server {server.server_id}] ==========")
            print(f"Served Requests: {server.total_requests_processed}")
            print(f"Dropped Requests Queue Full: {server.dropped_requests_queue_full}")
            print(f"Dropped Requests Process Timeout: {server.dropped_requests_process_timeout}")
            print(f"Dropped Requests High Load: {server.dropped_requests_high_load}")

        print()
        print("=========== FINAL SIMULATION OUTCOMES ==========")
        print(f"Total Requests Generated: {self.total_generated_requests}")
        print(f"Total Served Requests: {self.total_requests_served}")
        print(f"Total Drops (Queue Full): {self.total_requests_dropped_queue_full}")
        print(f"Total Drops (Process Timeout): {self.total_requests_dropped_process_timeout}")
        print(f"Total Drops (High Load): {self.total_requests_dropped_high_load}")
        print(f"Total Drops (No Server Available): {self.total_requests_dropped_network_down}")
        print(f"All Requests Accounted For: {self.total_requests_accounted_for == self.total_generated_requests}")

        total_accounted = (self.total_requests_served +
                           self.total_requests_dropped_queue_full +
                           self.total_requests_dropped_process_timeout +
                           self.total_requests_dropped_high_load +
                           self.total_requests_dropped_network_down)

        assert total_accounted == self.total_generated_requests, (f"Discrepancy Detected: {self.total_generated_requests} requests generated vs. "
                                                                  f"{total_accounted} requests accounted for.")

    """
    Cleans up any remaining requests that were still in the simulation pipeline at the end of the simulation.
    (i.e.: If 50,000 requests are generated in X timeframe, but at the end of X 5,000 are still in pipeline, results will not properly
    capture the full simulation snapshot due to data being cutoff)
    """
    def cleanup_remaining_requests(self):

        for server in self.target_network.network_servers:
            #Counts the remaining request as timeout requests as they could not be processed in the simulation timeframe
            remaining_in_queue = len(server.request_queue.items)
            server.dropped_requests_process_timeout += remaining_in_queue

            #Counts any requests that were being processed by a worker process as processed requests as it
            # would've been marked served if had not been cut off by simulation timeframe
            in_progress = server.request_process_worker.count
            server.total_requests_processed += in_progress

            #Adds up simulation totals
            self.total_requests_served += server.total_requests_processed
            self.total_requests_dropped_queue_full += server.dropped_requests_queue_full
            self.total_requests_dropped_process_timeout += server.dropped_requests_process_timeout
            self.total_requests_dropped_high_load += server.dropped_requests_high_load

        # Include network-wide drops (requests rejected because no servers online)
        self.total_requests_dropped_network_down = self.target_network.dropped_no_server_available

        self.total_generated_requests = self.target_network.incoming_request_count
        self.total_requests_accounted_for = (self.total_requests_served + self.total_requests_dropped_queue_full + self.total_requests_dropped_process_timeout
                                             + self.total_requests_dropped_high_load + self.total_requests_dropped_network_down)