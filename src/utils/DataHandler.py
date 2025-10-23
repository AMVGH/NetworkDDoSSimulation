import simpy
import csv
import os

from datetime import datetime
from src.models.Network import Network
from src.models.LegitimateTrafficNetwork import LegitimateTrafficNetwork
from src.models.Botnet import Botnet
from src.config import *
from src.utils.ProbabilityEngine import ProbabilityEngine, ProbabilityMetrics


class DataHandler:
    def __init__(self, env: simpy.Environment, target_network: Network, botnet: Botnet,
                 legitimate_traffic_network: LegitimateTrafficNetwork):
        self.env = env
        self.target_network = target_network
        self.botnet = botnet
        self.legitimate_traffic_network = legitimate_traffic_network

        # Houses probability algorithms
        self.probability_engine = ProbabilityEngine()

        # Simulation Total Metrics
        self.total_generated_requests = 0
        self.total_requests_accounted_for = 0
        self.total_requests_served = 0
        self.total_requests_dropped_queue_full = 0
        self.total_requests_dropped_process_timeout = 0
        self.total_requests_dropped_high_load = 0
        self.total_requests_dropped_network_down = 0

        # Time-Series Metrics
        self.simulation_series = {
            'timestamp': [],
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
                    'queue_length': [],  # Queue Depth
                    'active_workers': [],
                    'health_score': [],
                    'time_spent_offline': []
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

        self.probability_series = {
            'timestamp': [],
            'bandwidth_exhaustion_prob': [],
            'victim_resource_depletion_prob': [],
            'successful_attack_prob': []
        }

        # Track last values for rate calculations
        self.last_attack_calculation_time = 0
        self.last_total_malicious_requests = 0

    def start_data_collection(self):
        self.env.process(self.collect_simulation_data())
        self.env.process(self.collect_server_data())
        self.env.process(self.collect_legitimate_traffic_network_data())
        self.env.process(self.collect_malicious_traffic_network_data())
        self.env.process(self.collect_probability_data())

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

            yield self.env.timeout(INTERVAL_DATA_POLLING)

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

            yield self.env.timeout(INTERVAL_DATA_POLLING)

    def collect_server_data(self):
        while True:
            current_time = self.env.now

            for server in self.target_network.network_servers:
                server_id = server.server_id
                server_data = self.server_series[server_id]

                # Utilization
                server_data['utilization']['timestamp'].append(current_time)
                server_data['utilization']['cpu_utilization'].append(server.cpu_utilization)
                server_data['utilization']['queue_utilization'].append(server.process_queue_utilization)
                server_data['utilization']['queue_length'].append(len(server.request_queue.items))
                server_data['utilization']['active_workers'].append(server.request_process_worker.count)
                server_data['utilization']['health_score'].append(server.server_health)
                server_data['utilization']['time_spent_offline'].append(server.time_spent_offline)

                # Request Service
                server_data['service']['timestamp'].append(current_time)
                server_data['service']['total_requests_received'].append(server.total_requests_received)
                server_data['service']['total_requests_processed'].append(server.total_requests_processed)
                server_data['service']['total_requests_dropped_queue_full'].append(server.dropped_requests_queue_full)
                server_data['service']['total_requests_dropped_process_timeout'].append(server.dropped_requests_process_timeout)
                server_data['service']['total_requests_dropped_high_load'].append(server.dropped_requests_high_load)

            yield self.env.timeout(INTERVAL_DATA_POLLING)

    def collect_simulation_data(self):
        while True:
            current_time = self.env.now
            self.simulation_series['timestamp'].append(current_time)
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

            yield self.env.timeout(INTERVAL_DATA_POLLING)

    def collect_probability_data(self):
        while True:
            current_time = self.env.now

            current_attack_rate = self.calculate_current_attack_rate()
            memory_utilization = self.calculate_average_memory_utilization()
            successful_malicious_requests = sum(
                client.successful_response for client in self.botnet.network_clients
            )
            current_server_capacity = self.calculate_current_server_capacity()

            total_legit_sent = sum(
                client.requests_sent for client in self.legitimate_traffic_network.network_clients)
            total_legit_success = sum(
                client.successful_response for client in self.legitimate_traffic_network.network_clients)
            legitimate_success_rate = total_legit_success / max(1, total_legit_sent)

            simulation_state = {
                'current_attack_rate': current_attack_rate,
                'memory_utilization': memory_utilization,
                'successful_malicious_requests': successful_malicious_requests,
                'current_server_capacity': current_server_capacity,
                'legitimate_success_rate': legitimate_success_rate
            }

            probability_metrics = self.probability_engine.update_probabilities(
                simulation_state, current_time
            )

            self.probability_series['timestamp'].append(current_time)
            self.probability_series['bandwidth_exhaustion_prob'].append(
                probability_metrics.bandwidth_exhaustion_prob
            )
            self.probability_series['victim_resource_depletion_prob'].append(
                probability_metrics.victim_resource_depletion_prob
            )
            self.probability_series['successful_attack_prob'].append(
                probability_metrics.successful_attack_prob
            )

            yield self.env.timeout(INTERVAL_DATA_POLLING)

    def calculate_current_attack_rate(self) -> float:
        if not self.botnet.network_clients:
            return 0.0

        current_total = sum(client.requests_sent for client in self.botnet.network_clients)
        time_diff = self.env.now - self.last_attack_calculation_time

        if time_diff > 0:
            requests_diff = current_total - self.last_total_malicious_requests
            actual_rate = requests_diff / time_diff
        else:
            actual_rate = MALICIOUS_TRAFFIC_RATE * MALICIOUS_CLIENT_COUNT

        self.last_attack_calculation_time = self.env.now
        self.last_total_malicious_requests = current_total

        return actual_rate

    def calculate_average_memory_utilization(self) -> float:
        if not self.target_network.network_servers:
            return 0.0
        total_utilization = sum(server.cpu_utilization for server in self.target_network.network_servers)
        return total_utilization / len(self.target_network.network_servers)

    def calculate_current_server_capacity(self) -> float:
        online_servers = [s for s in self.target_network.network_servers if s.server_health > 0]
        return len(online_servers) * PROCESSING_POWER

    def cleanup_remaining_requests(self):
        for server in self.target_network.network_servers:
            # Counts the remaining request as timeout requests as they could not be processed in the simulation timeframe
            remaining_in_queue = len(server.request_queue.items)
            server.dropped_requests_process_timeout += remaining_in_queue

            # Counts any requests that were being processed by a worker process as processed requests as it
            # would've been marked served if had not been cut off by simulation timeframe
            in_progress = server.request_process_worker.count
            server.total_requests_processed += in_progress

            # Adds up simulation totals
            self.total_requests_served += server.total_requests_processed
            self.total_requests_dropped_queue_full += server.dropped_requests_queue_full
            self.total_requests_dropped_process_timeout += server.dropped_requests_process_timeout
            self.total_requests_dropped_high_load += server.dropped_requests_high_load

        # Include network-wide drops (requests rejected because no servers online)
        self.total_requests_dropped_network_down = self.target_network.dropped_no_server_available

        self.total_generated_requests = self.target_network.incoming_request_count
        self.total_requests_accounted_for = (self.total_requests_served + self.total_requests_dropped_queue_full +
                                             self.total_requests_dropped_process_timeout +
                                             self.total_requests_dropped_high_load + self.total_requests_dropped_network_down)

    def print_final_outcomes(self):
        self.print_probability_analysis()
        self.print_metrics_at_intervals(interval=INTERVAL_OUTPUT_POLLING)
        self.print_simulation_outcomes()

    def print_simulation_outcomes(self):
        print("\n" + "=" * 60)
        print("SIMULATION OUTCOMES BY SERVER")
        print("=" * 60)
        for server in self.target_network.network_servers:
            print("\n" + "=" * 60)
            print(f"SIMULATION OUTCOMES [Server {server.server_id}]")
            print("=" * 60)
            print(f"Time Spent Offline: {server.time_spent_offline:.4f} time units (seconds)")
            print(f"Requests Received: {server.total_requests_received}")
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
        print("\n" + "=" * 60)
        print("TIME-SERIES METRICS AT INTERVALS")
        print("=" * 60)

        if not self.simulation_series['timestamp']:
            print("No data collected yet.")
            return

        max_time = max(self.simulation_series['timestamp'])
        intervals = [t for t in self.simulation_series['timestamp'] if t % interval == 0]

        if not intervals:
            print(f"No data points at exact {interval}-second intervals.")
            intervals = [self.simulation_series['timestamp'][0]]  # Print at least first data point

        for interval_time in intervals:
            self.print_interval_metrics(interval_time)

    def print_interval_metrics(self, interval_time):
        print(f"\n" + "=" * 60)
        print(f"METRICS AT TIME: {interval_time:.1f}")
        print("=" * 60)

        sim_idx = self.find_index_for_time(self.simulation_series['timestamp'], interval_time)
        legit_idx = self.find_index_for_time(self.legitimate_network_series['timestamp'], interval_time)
        botnet_idx = self.find_index_for_time(self.botnet_series['timestamp'], interval_time)
        prob_idx = self.find_index_for_time(self.probability_series['timestamp'], interval_time)

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

        # DDoS Attack Probability Metrics
        if prob_idx is not None:
            print(f"\n=== DDoS ATTACK PROBABILITIES ===")
            print(f"  Bandwidth Exhaustion: {self.probability_series['bandwidth_exhaustion_prob'][prob_idx]:.2%}")
            print(f"  Resource Depletion: {self.probability_series['victim_resource_depletion_prob'][prob_idx]:.2%}")
            print(f"  Successful Attack: {self.probability_series['successful_attack_prob'][prob_idx]:.2%}")

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

        # Server metrics - USE TIME-SERIES DATA FOR INTERVALS
        print(f"\n=== SERVER STATUS ===")
        for server_id, server_data in self.server_series.items():
            idx = self.find_index_for_time(server_data['utilization']['timestamp'], interval_time)

            if idx is not None:
                print(f"\n  Server [{server_id}]:")
                print(f"    CPU Utilization: {server_data['utilization']['cpu_utilization'][idx]:.2%}")
                print(f"    Queue Utilization: {server_data['utilization']['queue_utilization'][idx]:.2%}")
                print(f"    Queue Length: {server_data['utilization']['queue_length'][idx]}")
                print(f"    Active Workers: {server_data['utilization']['active_workers'][idx]}")
                print(f"    Health Score: {server_data['utilization']['health_score'][idx]:.3f}")
                print(f"    Requests Received: {server_data['service']['total_requests_received'][idx]}")
                print(f"    Requests Processed: {server_data['service']['total_requests_processed'][idx]}")
                print(f"    Drops - Queue Full: {server_data['service']['total_requests_dropped_queue_full'][idx]}")
                print(f"    Drops - Timeout: {server_data['service']['total_requests_dropped_process_timeout'][idx]}")
                print(f"    Drops - High Load: {server_data['service']['total_requests_dropped_high_load'][idx]}")

    def print_probability_analysis(self):
        print("\n" + "=" * 60)
        print("DDoS ATTACK PROBABILITY ANALYSIS")
        print("=" * 60)

        avg_probs = self.probability_engine.get_average_probabilities()
        capacity_info = self.probability_engine.get_system_capacity_info()

        print(f"\nSystem Capacity Info:")
        print(f"  Total Processing: {capacity_info['total_processing_capacity']} req/sec")
        print(f"  Capacity Threshold: {capacity_info['capacity_threshold']} req/sec")

        print(f"\nAverage Probabilities Over Simulation:")
        print(f"  Bandwidth Exhaustion: {avg_probs['bandwidth_exhaustion_probability']:.2%}")
        print(f"  Resource Depletion: {avg_probs['victim_resource_depletion_probability']:.2%}")
        print(f"  Successful Attack: {avg_probs['successful_attack_probability']:.2%}")

        trends = self.probability_engine.get_probability_trend()
        if trends['bandwidth_exhaustion']:
            print(f"\nRecent Probability Trends:")
            print(f"  Bandwidth Exhaustion: {trends['bandwidth_exhaustion'][-1]:.2%}")
            print(f"  Resource Depletion: {trends['resource_depletion'][-1]:.2%}")
            print(f"  Successful Attack: {trends['successful_attack'][-1]:.2%}")

    def find_index_for_time(self, time_series, target_time, tolerance=0.1):
        if not time_series:
            return None
        for i, time_val in enumerate(time_series):
            if abs(time_val - target_time) <= tolerance:
                return i
        return None

    #TODO: Update Headers and Document
    def export_to_csv(self):
        #Create output directory
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        #Create output file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{output_dir}/Run{RUN_ID}_NetworkDDoSSimulation_Consolidated_Outcomes.csv"

        #Open and write to the .csv file
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header section
            writer.writerow(["Network DDoS Simulation Results"])
            writer.writerow(["Timestamp", timestamp])

            #Access config variables and headers for general simulation detail reporting
            config_vars = {
                "Simulation Duration": ("SIMULATION_DURATION", "Unknown"),
                "Number of Servers": ("NUM_SERVERS", "Unknown"),
                "Processing Power": ("PROCESSING_POWER", "Unknown"),
                "Queue Size": ("MAX_REQUEST_QUEUE_LENGTH", "Unknown"),
                "Legitimate Clients": ("LEGITIMATE_CLIENT_COUNT", "Unknown"),
                "Malicious Clients": ("MALICIOUS_CLIENT_COUNT", "Unknown"),
                "Legitimate Traffic Rate": ("LEGITIMATE_TRAFFIC_RATE", "Unknown"),
                "Malicious Traffic Rate": ("MALICIOUS_TRAFFIC_RATE", "Unknown"),
                "Request Timeout": ("REQUEST_TIMEOUT", "Unknown"),
                "Server Timeout": ("SERVER_TIMEOUT", "Unknown")
            }


            for label, (var_name, default) in config_vars.items():
                try:
                    value = globals().get(var_name, default)
                    if var_name in ["PROCESSING_POWER", "LEGITIMATE_TRAFFIC_RATE", "MALICIOUS_TRAFFIC_RATE"]:
                        writer.writerow([label, f"{value} req/sec"])
                    elif var_name in ["SIMULATION_DURATION", "REQUEST_TIMEOUT", "SERVER_TIMEOUT"]:
                        writer.writerow([label, f"{value}s"])
                    else:
                        writer.writerow([label, value])
                except NameError:
                    writer.writerow([label, default])

            writer.writerow([])

            #Final Simulation Results
            writer.writerow(["Final Simulation Results"])
            writer.writerow(["Total Generated Requests", self.total_generated_requests])
            writer.writerow(["Total Served Requests", self.total_requests_served])
            writer.writerow(["Total Dropped - Queue Full", self.total_requests_dropped_queue_full])
            writer.writerow(["Total Dropped - Timeout", self.total_requests_dropped_process_timeout])
            writer.writerow(["Total Dropped - High Load", self.total_requests_dropped_high_load])
            writer.writerow(["Total Dropped - No Server", self.total_requests_dropped_network_down])

            #Calculate the overall success rate as well as drop rate throughout the simulation lifetime
            overall_success_rate = (self.total_requests_served / max(1, self.total_generated_requests))
            total_drops = (self.total_requests_dropped_queue_full +
                           self.total_requests_dropped_process_timeout +
                           self.total_requests_dropped_high_load +
                           self.total_requests_dropped_network_down)
            overall_drop_rate = total_drops / max(1, self.total_generated_requests)

            #Include metrics in final simulation results
            writer.writerow(["Overall Success Rate", f"{overall_success_rate:.2%}"])
            writer.writerow(["Overall Drop Rate", f"{overall_drop_rate:.2%}"])
            writer.writerow([])

            #Display probability analysis (algorithms from expected results) as well as req/sec for total processing capacity and threshold
            avg_probs = self.probability_engine.get_average_probabilities()
            capacity_info = self.probability_engine.get_system_capacity_info()
            writer.writerow(["Probability Analysis"])
            writer.writerow(["Bandwidth Exhaustion", f"{avg_probs['bandwidth_exhaustion_probability']:.2%}"])
            writer.writerow(["Resource Depletion", f"{avg_probs['victim_resource_depletion_probability']:.2%}"])
            writer.writerow(["Successful Attack", f"{avg_probs['successful_attack_probability']:.2%}"])
            writer.writerow(["Total Processing Capacity", f"{capacity_info['total_processing_capacity']} req/sec"])
            writer.writerow(["Capacity Threshold", f"{capacity_info['capacity_threshold']} req/sec"])
            writer.writerow([])

            #Displays in-depth simulation results per server over the course of the simulation lifetime, does any and all relevant calculations to put data in final form
            writer.writerow(["Per-Server Breakdown"])
            server_headers = [
                "Server ID",
                "Total Requests Received", "Total Requests Processed",
                "Success Rate", "Acceptance Rate", "Processing Rate",
                "Drops Queue Full", "Drops Queue Full Rate",
                "Drops Timeout", "Drops Timeout Rate",
                "Drops High Load", "Drops High Load Rate",
                "Total Drops", "Total Drop Rate",
                "Max CPU Utilization", "Avg CPU Utilization",
                "Max Queue Utilization", "Avg Queue Utilization",
                "Max Queue Length", "Avg Queue Length",
                "Min Health Score", "Avg Health Score",
                "Time Spent Offline", "Offline Percentage",
            ]
            writer.writerow(server_headers)

            #Iterate over the servers
            for server in self.target_network.network_servers:
                server_id = server.server_id
                server_data = self.server_series.get(server_id, {})

                total_received = server.total_requests_received
                total_processed = server.total_requests_processed
                drops_queue_full = server.dropped_requests_queue_full
                drops_timeout = server.dropped_requests_process_timeout
                drops_high_load = server.dropped_requests_high_load

                success_rate = total_processed / max(1, total_received) if total_received > 0 else 0
                total_accepted = total_processed + drops_queue_full + drops_timeout + drops_high_load
                acceptance_rate = total_accepted / max(1, total_received) if total_received > 0 else 0
                processing_rate = total_processed / max(1, SIMULATION_DURATION) if SIMULATION_DURATION > 0 else 0

                drops_queue_full_rate = drops_queue_full / max(1, total_received) if total_received > 0 else 0
                drops_timeout_rate = drops_timeout / max(1, total_received) if total_received > 0 else 0
                drops_high_load_rate = drops_high_load / max(1, total_received) if total_received > 0 else 0

                total_drops = drops_queue_full + drops_timeout + drops_high_load
                total_drop_rate = total_drops / max(1, total_received) if total_received > 0 else 0

                #Metrics from the time series
                if server_data and server_data['utilization']['cpu_utilization']:
                    cpu_utils = server_data['utilization']['cpu_utilization']
                    queue_utils = server_data['utilization']['queue_utilization']
                    queue_lengths = server_data['utilization']['queue_length']
                    health_scores = server_data['utilization']['health_score']

                    max_cpu_util = max(cpu_utils) * 100
                    avg_cpu_util = (sum(cpu_utils) / len(cpu_utils)) * 100
                    max_queue_util = max(queue_utils) * 100
                    avg_queue_util = (sum(queue_utils) / len(queue_utils)) * 100
                    max_queue_length = max(queue_lengths)
                    avg_queue_length = sum(queue_lengths) / len(queue_lengths)
                    min_health = min(health_scores)
                    avg_health = sum(health_scores) / len(health_scores)
                else:
                    max_cpu_util = avg_cpu_util = max_queue_util = avg_queue_util = 0
                    max_queue_length = avg_queue_length = min_health = avg_health = 0

                #Gets server downtime and calculates the percentage
                time_spent_offline = getattr(server, 'time_spent_offline', 0)
                offline_percentage = (time_spent_offline / SIMULATION_DURATION) * 100 if SIMULATION_DURATION > 0 else 0

                server_row = [
                    server_id,
                    total_received,
                    total_processed,
                    f"{success_rate:.2%}",
                    f"{acceptance_rate:.2%}",
                    f"{processing_rate:.1f} req/sec",
                    drops_queue_full,
                    f"{drops_queue_full_rate:.2%}",
                    drops_timeout,
                    f"{drops_timeout_rate:.2%}",
                    drops_high_load,
                    f"{drops_high_load_rate:.2%}",
                    total_drops,
                    f"{total_drop_rate:.2%}",
                    f"{max_cpu_util:.1f}%",
                    f"{avg_cpu_util:.1f}%",
                    f"{max_queue_util:.1f}%",
                    f"{avg_queue_util:.1f}%",
                    max_queue_length,
                    f"{avg_queue_length:.1f}",
                    f"{min_health:.3f}",
                    f"{avg_health:.3f}",
                    f"{time_spent_offline:.1f}s",
                    f"{offline_percentage:.1f}%"
                ]
                writer.writerow(server_row)

            writer.writerow([])

            # Displays simulation time-series data across the entire simulation
            writer.writerow(["Total Simulation Time-Series Data"])
            time_series_headers = [
                "Timestamp",
                "Total Generated", "Total Served",
                "Drops Queue Full", "Drops Timeout", "Drops High Load", "Drops No Server",
                "Success Rate", "Drop Rate",
                "Legit Sent", "Legit Success", "Legit No Response", "Legit Success Rate", "Legit Drop Rate",
                "Botnet Sent", "Botnet Success", "Botnet No Response", "Botnet Success Rate", "Botnet Drop Rate",
                "Bandwidth Exhaustion Prob", "Resource Depletion Prob", "Successful Attack Prob",
                "Avg CPU Utilization", "Avg Queue Utilization", "Avg Health Score"
            ]
            writer.writerow(time_series_headers)

            max_data_points = len(self.simulation_series['timestamp'])
            for i in range(max_data_points):
                timestamp_val = self.simulation_series['timestamp'][i]

                # Calculate any relevant rates
                total_generated = self.simulation_series['total_generated'][i]
                total_served = self.simulation_series['total_served'][i]
                total_drops_interval = (self.simulation_series['total_drops_queue_full'][i] +
                                        self.simulation_series['total_drops_timeout'][i] +
                                        self.simulation_series['total_drops_high_load'][i] +
                                        self.simulation_series['total_drops_no_server'][i])

                success_rate = total_served / max(1, total_generated) if total_generated > 0 else 0
                drop_rate = total_drops_interval / max(1, total_generated) if total_generated > 0 else 0

                #Legitmate
                legit_sent = self.legitimate_network_series['requests_sent'][i] if i < len(
                    self.legitimate_network_series['requests_sent']) else 0
                legit_success = self.legitimate_network_series['successful_response'][i] if i < len(
                    self.legitimate_network_series['successful_response']) else 0
                legit_no_response = self.legitimate_network_series['no_response'][i] if i < len(
                    self.legitimate_network_series['no_response']) else 0
                legit_success_rate = legit_success / max(1, legit_sent) if legit_sent > 0 else 0
                legit_drop_rate = legit_no_response / max(1, legit_sent) if legit_sent > 0 else 0

                #Botnet
                botnet_sent = self.botnet_series['requests_sent'][i] if i < len(
                    self.botnet_series['requests_sent']) else 0
                botnet_success = self.botnet_series['successful_response'][i] if i < len(
                    self.botnet_series['successful_response']) else 0
                botnet_no_response = self.botnet_series['no_response'][i] if i < len(
                    self.botnet_series['no_response']) else 0
                botnet_success_rate = botnet_success / max(1, botnet_sent) if botnet_sent > 0 else 0
                botnet_drop_rate = botnet_no_response / max(1, botnet_sent) if botnet_sent > 0 else 0

                #Calculate relevant averages
                avg_cpu_util = 0
                avg_queue_util = 0
                avg_health_score = 0
                server_count = len(self.server_series)

                if server_count > 0:
                    cpu_utils = []
                    queue_utils = []
                    health_scores = []

                    for server_id, server_data in self.server_series.items():
                        if i < len(server_data['utilization']['timestamp']):
                            cpu_utils.append(server_data['utilization']['cpu_utilization'][i])
                            queue_utils.append(server_data['utilization']['queue_utilization'][i])
                            health_scores.append(server_data['utilization']['health_score'][i])

                    if cpu_utils:
                        avg_cpu_util = sum(cpu_utils) / len(cpu_utils)
                        avg_queue_util = sum(queue_utils) / len(queue_utils)
                        avg_health_score = sum(health_scores) / len(health_scores)

                #Accessing probability values
                bandwidth_prob = self.probability_series['bandwidth_exhaustion_prob'][i] if i < len(
                    self.probability_series['bandwidth_exhaustion_prob']) else 0
                resource_prob = self.probability_series['victim_resource_depletion_prob'][i] if i < len(
                    self.probability_series['victim_resource_depletion_prob']) else 0
                attack_prob = self.probability_series['successful_attack_prob'][i] if i < len(
                    self.probability_series['successful_attack_prob']) else 0

                row = [
                    timestamp_val,
                    total_generated,
                    total_served,
                    self.simulation_series['total_drops_queue_full'][i],
                    self.simulation_series['total_drops_timeout'][i],
                    self.simulation_series['total_drops_high_load'][i],
                    self.simulation_series['total_drops_no_server'][i],
                    success_rate,
                    drop_rate,
                    legit_sent,
                    legit_success,
                    legit_no_response,
                    legit_success_rate,
                    legit_drop_rate,
                    botnet_sent,
                    botnet_success,
                    botnet_no_response,
                    botnet_success_rate,
                    botnet_drop_rate,
                    bandwidth_prob,
                    resource_prob,
                    attack_prob,
                    f"{avg_cpu_util:.2%}",
                    f"{avg_queue_util:.2%}",
                    f"{avg_health_score:.3f}"
                ]
                writer.writerow(row)

            writer.writerow([])

            #Writes the same time-series data but per-server
            for server_id, server_data in self.server_series.items():
                writer.writerow([f"{server_id} Time-Series Data"])
                server_headers = [
                    "Timestamp",
                    "CPU Utilization", "Queue Utilization", "Queue Length",
                    "Active Workers", "Health Score",
                    "Requests Received", "Requests Processed",
                    "Drops Queue Full", "Drops Timeout", "Drops High Load",
                    "Processing Rate", "Drop Rate", "Success Rate",
                    "Time Spent Offline", "Offline Percentage"
                ]
                writer.writerow(server_headers)

                max_server_points = len(server_data['utilization']['timestamp'])
                for i in range(max_server_points):
                    timestamp_val = server_data['utilization']['timestamp'][i]

                    #Calculate relevant rates
                    requests_received = server_data['service']['total_requests_received'][i] if i < len(
                        server_data['service']['total_requests_received']) else 0
                    requests_processed = server_data['service']['total_requests_processed'][i] if i < len(
                        server_data['service']['total_requests_processed']) else 0
                    drops_queue_full = server_data['service']['total_requests_dropped_queue_full'][i] if i < len(
                        server_data['service']['total_requests_dropped_queue_full']) else 0
                    drops_timeout = server_data['service']['total_requests_dropped_process_timeout'][i] if i < len(
                        server_data['service']['total_requests_dropped_process_timeout']) else 0
                    drops_high_load = server_data['service']['total_requests_dropped_high_load'][i] if i < len(
                        server_data['service']['total_requests_dropped_high_load']) else 0

                    total_drops_server = drops_queue_full + drops_timeout + drops_high_load
                    success_rate_server = requests_processed / max(1, requests_received) if requests_received > 0 else 0
                    drop_rate_server = total_drops_server / max(1, requests_received) if requests_received > 0 else 0

                    #Calculate processing rate (requests per second since last interval)
                    processing_rate = 0
                    if i > 0 and i < len(server_data['utilization']['timestamp']):
                        time_diff = server_data['utilization']['timestamp'][i] - \
                                    server_data['utilization']['timestamp'][i - 1]
                        if time_diff > 0:
                            processed_diff = requests_processed - (
                                server_data['service']['total_requests_processed'][i - 1] if i - 1 < len(
                                    server_data['service']['total_requests_processed']) else 0)
                            processing_rate = processed_diff / time_diff

                    #Get offline metrics for this time interval
                    time_spent_offline = server_data['utilization']['time_spent_offline'][i] if i < len(
                        server_data['utilization']['time_spent_offline']) else 0
                    offline_percentage = (time_spent_offline / timestamp_val) * 100 if timestamp_val > 0 else 0

                    server_row = [
                        timestamp_val,
                        f"{server_data['utilization']['cpu_utilization'][i]:.2%}",
                        f"{server_data['utilization']['queue_utilization'][i]:.2%}",
                        server_data['utilization']['queue_length'][i],
                        server_data['utilization']['active_workers'][i],
                        f"{server_data['utilization']['health_score'][i]:.3f}",
                        requests_received,
                        requests_processed,
                        drops_queue_full,
                        drops_timeout,
                        drops_high_load,
                        f"{processing_rate:.1f} req/sec",
                        f"{drop_rate_server:.2%}",
                        f"{success_rate_server:.2%}",
                        f"{time_spent_offline:.1f}s",
                        f"{offline_percentage:.1f}%"
                    ]
                    writer.writerow(server_row)

                writer.writerow([])

            print(f"\nComprehensive CSV export completed: {filename}")