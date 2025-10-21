import simpy

from src.models.Network import Network
from src.models.LegitimateTrafficNetwork import LegitimateTrafficNetwork
from src.models.Botnet import Botnet

#TODO: Build output mechanisms for CSV, JSON, etc. --> Possibly do Data Calc --> revisit if best assert implementation

class DataCollector:
    def __init__(self, env: simpy.Environment, target_network: Network, botnet: Botnet, legitimate_traffic_network: LegitimateTrafficNetwork):
        self.env = env
        self.target_network = target_network
        self.botnet = botnet
        self.legitimate_traffic_network = legitimate_traffic_network

        #Simulation Total Metrics
        self.total_generated_requests = 0
        self.total_requests_accounted_for = 0
        self.total_requests_served = 0
        self.total_requests_dropped_queue_full = 0
        self.total_requests_dropped_process_timeout = 0
        self.total_requests_dropped_high_load = 0
        self.total_requests_dropped_network_down = 0

        #Time-Series Metrics
        self.simulation_series = {
            'time': [],
            'total_generated': [],
            'total_served': [],
            'total_drops_queue_full': [],
            'total_drops_timeout': [],
            'total_drops_high_load': [],
            'total_drops_no_server': []
        }

        self.legitimate_network_series = {
            'timestamp': [],
            'requests_sent': [],
            'successful_response': [],
            'no_response': []
        }

        self.botnet_series = {
            'timestamp': [],
            'requests_sent': [],
            'successful_response': [],
            'no_response': []
        }

        self.server_series = {}
        for server in self.target_network.network_servers:
            self.server_series[server.server_id] = {
                'utilization': {
                    'timestamp': [],
                    'cpu_utilization': [],
                    'queue_utilization': [],
                    'queue_length': [], #Queue Depth
                    'active_workers': [],
                    'health_score': []
                },
                'service': {
                    'timestamp': [],
                    'total_requests_received': [],
                    'total_requests_processed': [],
                    'total_requests_dropped_queue_full': [],
                    'total_requests_dropped_process_timeout': [],
                    'total_requests_dropped_high_load': []
                }
            }

    def start_data_collection(self):
        self.env.process(self.collect_simulation_data())
        self.env.process(self.collect_server_data())
        self.env.process(self.collect_legitimate_traffic_network_data())
        self.env.process(self.collect_malicious_traffic_network_data())

    def collect_legitimate_traffic_network_data(self):
        while True:
            current_time = self.env.now

            total_requests_sent = 0
            total_successful_response = 0
            total_no_response = 0

            for legitimate_client in self.legitimate_traffic_network.network_clients:
                total_requests_sent += legitimate_client.requests_sent
                total_successful_response += legitimate_client.successful_response
                total_no_response += legitimate_client.no_response

            self.legitimate_network_series['timestamp'].append(current_time)
            self.legitimate_network_series['requests_sent'].append(total_requests_sent)
            self.legitimate_network_series['successful_response'].append(total_successful_response)
            self.legitimate_network_series['no_response'].append(total_no_response)

            yield self.env.timeout(1.0)

    def collect_malicious_traffic_network_data(self):
        while True:
            current_time = self.env.now

            total_requests_sent = 0
            total_successful_response = 0
            total_no_response = 0

            for malicious_client in self.botnet.network_clients:
                total_requests_sent += malicious_client.requests_sent
                total_successful_response += malicious_client.successful_response
                total_no_response += malicious_client.no_response

            self.botnet_series['timestamp'].append(current_time)
            self.botnet_series['requests_sent'].append(total_requests_sent)
            self.botnet_series['successful_response'].append(total_successful_response)
            self.botnet_series['no_response'].append(total_no_response)

            yield self.env.timeout(1.0)

    def collect_server_data(self):
        while True:
            current_time = self.env.now

            for server in self.target_network.network_servers:
                server_id = server.server_id
                server_data = self.server_series[server_id]

                #Utilization
                server_data['utilization']['timestamp'].append(current_time)
                server_data['utilization']['cpu_utilization'].append(server.cpu_utilization)
                server_data['utilization']['queue_utilization'].append(server.process_queue_utilization)
                server_data['utilization']['queue_length'].append(len(server.request_queue.items))
                server_data['utilization']['active_workers'].append(server.request_process_worker.count)
                server_data['utilization']['health_score'].append(server.server_health)

                #Request Service
                server_data['service']['timestamp'].append(current_time)
                server_data['service']['total_requests_received'].append(server.total_requests_received)
                server_data['service']['total_requests_processed'].append(server.total_requests_processed)
                server_data['service']['total_requests_dropped_queue_full'].append(server.dropped_requests_queue_full)
                server_data['service']['total_requests_dropped_process_timeout'].append(server.dropped_requests_process_timeout)
                server_data['service']['total_requests_dropped_high_load'].append(server.dropped_requests_high_load)
            yield self.env.timeout(1.0)

    def collect_simulation_data(self):
        while True:
            current_time = self.env.now

            self.simulation_series['time'].append(current_time)
            self.simulation_series['total_generated'].append(self.target_network.incoming_request_count)
            self.simulation_series['total_served'].append(
                sum(s.total_requests_processed for s in self.target_network.network_servers))
            self.simulation_series['total_drops_queue_full'].append(
                sum(s.dropped_requests_queue_full for s in self.target_network.network_servers))
            self.simulation_series['total_drops_timeout'].append(
                sum(s.dropped_requests_process_timeout for s in self.target_network.network_servers))
            self.simulation_series['total_drops_high_load'].append(
                sum(s.dropped_requests_high_load for s in self.target_network.network_servers))
            self.simulation_series['total_drops_no_server'].append(self.target_network.dropped_no_server_available)

            yield self.env.timeout(1.0)

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

    def print_simulation_outcomes(self):
        print("\n" + "=" * 60)
        print("SIMULATION OUTCOMES BY SERVER")
        print("=" * 60)
        for server in self.target_network.network_servers:
            print("\n" + "=" * 60)
            print(f"SIMULATION OUTCOMES [Server {server.server_id}]")
            print("=" * 60)
            print(f"Served Requests: {server.total_requests_processed}")
            print(f"Dropped Requests Queue Full: {server.dropped_requests_queue_full}")
            print(f"Dropped Requests Process Timeout: {server.dropped_requests_process_timeout}")
            print(f"Dropped Requests High Load: {server.dropped_requests_high_load}")

        total_accounted = (self.total_requests_served +
                           self.total_requests_dropped_queue_full +
                           self.total_requests_dropped_process_timeout +
                           self.total_requests_dropped_high_load +
                           self.total_requests_dropped_network_down)

        print("\n" + "=" * 60)
        print("FINAL SIMULATION OUTCOMES")
        print("=" * 60)
        print()
        print(f"Total Requests Generated: {self.total_generated_requests}")
        print(f"Total Served Requests: {self.total_requests_served}")
        print(f"Total Drops (Queue Full): {self.total_requests_dropped_queue_full}")
        print(f"Total Drops (Process Timeout): {self.total_requests_dropped_process_timeout}")
        print(f"Total Drops (High Load): {self.total_requests_dropped_high_load}")
        print(f"Total Drops (No Server Available): {self.total_requests_dropped_network_down}")
        print(f"All Requests Accounted For: {self.total_requests_accounted_for == self.total_generated_requests}")

        assert total_accounted == self.total_generated_requests, (
            f"Discrepancy Detected: {self.total_generated_requests} requests generated vs. "
            f"{total_accounted} requests accounted for.")

    def print_metrics_at_intervals(self, interval=10):
        """Print all metrics at specified time intervals"""
        print("\n" + "=" * 60)
        print("TIME-SERIES METRICS AT INTERVALS")
        print("=" * 60)

        # Find all time indices that are multiples of the interval
        if not self.simulation_series['time']:
            print("No data collected yet.")
            return

        max_time = max(self.simulation_series['time'])
        intervals = [t for t in self.simulation_series['time'] if t % interval == 0]

        if not intervals:
            print(f"No data points at exact {interval}-second intervals.")
            intervals = [self.simulation_series['time'][0]]  # Print at least first data point

        for interval_time in intervals:
            self._print_interval_metrics(interval_time)

    def _print_interval_metrics(self, interval_time):
        """Print metrics for a specific time interval"""
        print(f"\n" + "=" * 60)
        print(f"METRICS AT TIME: {interval_time:.1f}")
        print("=" * 60)

        # Find index for this time in simulation series
        sim_idx = self._find_index_for_time(self.simulation_series['time'], interval_time)
        legit_idx = self._find_index_for_time(self.legitimate_network_series['timestamp'], interval_time)
        botnet_idx = self._find_index_for_time(self.botnet_series['timestamp'], interval_time)

        # Simulation-level metrics
        if sim_idx is not None:
            print(f"\n=== SIMULATION OVERVIEW ===")
            print(f"  Total Generated: {self.simulation_series['total_generated'][sim_idx]}")
            print(f"  Total Served: {self.simulation_series['total_served'][sim_idx]}")
            print(f"  Drops - Queue Full: {self.simulation_series['total_drops_queue_full'][sim_idx]}")
            print(f"  Drops - Timeout: {self.simulation_series['total_drops_timeout'][sim_idx]}")
            print(f"  Drops - High Load: {self.simulation_series['total_drops_high_load'][sim_idx]}")
            print(f"  Drops - No Server: {self.simulation_series['total_drops_no_server'][sim_idx]}")

            total_drops = (self.simulation_series['total_drops_queue_full'][sim_idx] +
                           self.simulation_series['total_drops_timeout'][sim_idx] +
                           self.simulation_series['total_drops_high_load'][sim_idx] +
                           self.simulation_series['total_drops_no_server'][sim_idx])

            success_rate = (self.simulation_series['total_served'][sim_idx] /
                            max(1, self.simulation_series['total_generated'][sim_idx]))
            print(f"  Success Rate: {success_rate:.2%}")
            print(f"  Drop Rate: {total_drops / max(1, self.simulation_series['total_generated'][sim_idx]):.2%}")

        # Legitimate traffic metrics
        if legit_idx is not None:
            print(f"\n=== LEGITIMATE TRAFFIC ===")
            print(f"  Requests Sent: {self.legitimate_network_series['requests_sent'][legit_idx]}")
            print(f"  Successful: {self.legitimate_network_series['successful_response'][legit_idx]}")
            print(f"  No Response: {self.legitimate_network_series['no_response'][legit_idx]}")

            legit_success_rate = (self.legitimate_network_series['successful_response'][legit_idx] /
                                  max(1, self.legitimate_network_series['requests_sent'][legit_idx]))
            print(f"  Success Rate: {legit_success_rate:.2%}")

        # Botnet traffic metrics
        if botnet_idx is not None:
            print(f"\n=== BOTNET TRAFFIC ===")
            print(f"  Requests Sent: {self.botnet_series['requests_sent'][botnet_idx]}")
            print(f"  Successful: {self.botnet_series['successful_response'][botnet_idx]}")
            print(f"  No Response: {self.botnet_series['no_response'][botnet_idx]}")

            botnet_success_rate = (self.botnet_series['successful_response'][botnet_idx] /
                                   max(1, self.botnet_series['requests_sent'][botnet_idx]))
            print(f"  Success Rate: {botnet_success_rate:.2%}")

        # Server metrics
        print(f"\n=== SERVER STATUS ===")
        for server_id, server_data in self.server_series.items():
            util_idx = self._find_index_for_time(server_data['utilization']['timestamp'], interval_time)
            service_idx = self._find_index_for_time(server_data['service']['timestamp'], interval_time)

            if util_idx is not None and service_idx is not None:
                print(f"\n  Server [{server_id}]:")
                print(f"    CPU Utilization: {server_data['utilization']['cpu_utilization'][util_idx]:.2%}")
                print(f"    Queue Utilization: {server_data['utilization']['queue_utilization'][util_idx]:.2%}")
                print(f"    Queue Length: {server_data['utilization']['queue_length'][util_idx]}")
                print(f"    Active Workers: {server_data['utilization']['active_workers'][util_idx]}")
                print(f"    Health Score: {server_data['utilization']['health_score'][util_idx]:.3f}")
                print(f"    Requests Received: {server_data['service']['total_requests_received'][service_idx]}")
                print(f"    Requests Processed: {server_data['service']['total_requests_processed'][service_idx]}")
                print(
                    f"    Drops - Queue Full: {server_data['service']['total_requests_dropped_queue_full'][service_idx]}")
                print(
                    f"    Drops - Timeout: {server_data['service']['total_requests_dropped_process_timeout'][service_idx]}")
                print(
                    f"    Drops - High Load: {server_data['service']['total_requests_dropped_high_load'][service_idx]}")

    def _find_index_for_time(self, time_series, target_time, tolerance=0.1):
        if not time_series:
            return None

        # Find exact match or closest within tolerance
        for i, time_val in enumerate(time_series):
            if abs(time_val - target_time) <= tolerance:
                return i

        return None