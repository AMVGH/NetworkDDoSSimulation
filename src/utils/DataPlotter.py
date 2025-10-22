import matplotlib.pyplot as plot
from src.utils.DataCollector import DataCollector

# TODO: Implement to Calculate Expected vs. Actual
# - Probability of Depletion of Bandwidth Exhaustion
# - Probability of Depletion of Victim Resources
# - Probability of Successful Attack

class DataPlotter:
    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector

    def visualize_all_results(self):
        #Allows multiple windows to be displayed at once
        plot.ion()

        #Creates the windows to display simulation graph data
        self.create_server_utilization_window()
        self.create_request_generation_rate_versus_served_rate_window()
        self.create_request_service_window()
        self.create_request_traffic_comparison_window()

        #Disables interactive mode and displays plot windows
        plot.ioff()
        plot.show()

    # Dashboard Region
    def create_request_generation_rate_versus_served_rate_window(self):
        fig, ax = plot.subplots(figsize=(12, 6))


        timestamps = self.data_collector.simulation_series['timestamp']
        total_generated = self.data_collector.simulation_series['total_generated']
        total_served = self.data_collector.simulation_series['total_served']

        generation_rates = []
        serving_rates = []

        #Generates and populates the generation rate of requests as well as the serving rates
        for i in range(1, len(timestamps)):
            time_diff = timestamps[i] - timestamps[i - 1]
            gen_diff = total_generated[i] - total_generated[i - 1]
            served_diff = total_served[i] - total_served[i - 1]

            generation_rates.append(gen_diff / time_diff if time_diff > 0 else 0)
            serving_rates.append(served_diff / time_diff if time_diff > 0 else 0)

        # Plot the rates
        ax.plot(timestamps[1:], generation_rates, label='Request Generation Rate', linewidth=2, color='red')
        ax.plot(timestamps[1:], serving_rates, label='Request Serve Rate', linewidth=2, color='blue')
        ax.set_title('Request Servicing: Request Generation Rate vs Serve Rate Over Time', fontsize=16, fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Requests per Second')
        ax.legend()
        ax.grid(True, alpha=0.3)

        #Helper method and window layout
        fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event, fig))
        plot.tight_layout()

    def create_server_utilization_window(self):
        #Defines subplots to be visualized within the utilization window
        fig, (ax1, ax2, ax3) = plot.subplots(3, 1, figsize=(12, 10))
        fig.suptitle('Server Utilization: CPU Utilization, Queue Utilization, and Queue Depth', fontsize=16, fontweight='bold')

        #Subplots
        self.graph_queue_length_by_server(ax1)
        self.graph_queue_utilization_by_server(ax2)
        self.graph_cpu_utilization_by_server(ax3)

        #Subplot layout and adjustment
        plot.tight_layout()
        plot.subplots_adjust(top=0.93)

        #Hover helper method to help with data visualization and conceptualization
        fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event, fig))

    def create_request_service_window(self):
        #Defines subplots to be visualized within the request service window
        fig, (ax1, ax2, ax3) = plot.subplots(3, 1, figsize=(12, 10))
        fig.suptitle('Request Servicing: Legitimate Throughput, Legitimate Drop Rate, and Total Drop Rate Pattern', fontsize=16, fontweight='bold')

        #Subplots
        self.graph_legitimate_throughput(ax1)
        self.graph_legitimate_drop_rate(ax2)
        self.graph_total_drop_patterns(ax3)

        #Subplot layout and adjustment
        plot.tight_layout()
        plot.subplots_adjust(top=0.93)

        #Hover helper method to help with data visualization and conceptualization
        fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event, fig))

    def create_request_traffic_comparison_window(self):
        #Defines subplots to be visualized within the request comparison window
        fig, (ax1, ax2, ax3) = plot.subplots(3, 1, figsize=(12, 10))
        fig.suptitle('Generation Comparison: Legitimate vs Malicious Traffic Comparison, Success Rates, and Server Health', fontsize=16, fontweight='bold')

        #Subplots
        self.graph_traffic_generation_rates(ax1)
        self.graph_traffic_success_rates(ax2)
        self.graph_server_health_by_server(ax3)

        #Subplot layout and adjustment
        plot.tight_layout()
        plot.subplots_adjust(top=0.93)

        #Hover helper method to help with data visualization and conceptualization
        fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event, fig))

    #Individual Graph Region
    """
    Plots the throughput of legitimate requests against the timestamps in the legitimate_network_series collection
    """
    def graph_legitimate_throughput(self,ax):
        timestamps = self.data_collector.legitimate_network_series['timestamp']
        successful_responses = self.data_collector.legitimate_network_series['successful_response']

        throughput = []
        for i in range(1, len(timestamps)):
            time_diff = timestamps[i] - timestamps[i - 1]
            success_diff = successful_responses[i] - successful_responses[i - 1]
            throughput.append(success_diff / time_diff if time_diff > 0 else 0)

        ax.plot(timestamps[1:], throughput, label='Legitimate Throughput', linewidth=2, color='green')
        ax.set_title('Legitimate Request Throughput Over Time', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Throughput (successful requests/sec)')
        ax.grid(True, alpha=0.3)
        ax.legend()

    """
    Plots the rate of legitimate dropped requests against the timestamps in the legitimate_network_series collection
    """
    def graph_legitimate_drop_rate(self, ax):
        timestamps = self.data_collector.legitimate_network_series['timestamp']
        requests_sent = self.data_collector.legitimate_network_series['requests_sent']
        no_response = self.data_collector.legitimate_network_series['no_response']

        drop_rates = []
        for i in range(len(timestamps)):
            if requests_sent[i] > 0:
                drop_rate = (no_response[i] / requests_sent[i]) * 100
            else:
                drop_rate = 0
            drop_rates.append(drop_rate)

        ax.plot(timestamps, drop_rates, label='Legitimate Drop Rate', linewidth=2, color='red')
        ax.set_title('Legitimate Request Drop Rate Over Time', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Drop Rate (%)')
        ax.grid(True, alpha=0.3)
        ax.legend()

    """
    Plots the total drop patterns of simulation_series against the timestamps
    """
    def graph_total_drop_patterns(self, ax):
        timestamps = self.data_collector.simulation_series['timestamp']
        total_generated = self.data_collector.simulation_series['total_generated']

        # Calculate total drops at each time point
        total_drops = []
        for i in range(len(timestamps)):
            drops = (self.data_collector.simulation_series['total_drops_queue_full'][i] +
                     self.data_collector.simulation_series['total_drops_timeout'][i] +
                     self.data_collector.simulation_series['total_drops_high_load'][i] +
                     self.data_collector.simulation_series['total_drops_no_server'][i])
            total_drops.append(drops)

        # Calculate drop rate percentage
        drop_rates = []
        for i in range(len(timestamps)):
            if total_generated[i] > 0:
                drop_rate = (total_drops[i] / total_generated[i]) * 100
            else:
                drop_rate = 0
            drop_rates.append(drop_rate)

        ax.plot(timestamps, drop_rates, label='Total Drop Rate', linewidth=2, color='orange')
        ax.set_title('Total Request Drop Rate Patterns', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Drop Rate (%)')
        ax.grid(True, alpha=0.3)
        ax.legend()

    """
    Plots the queue lengths for servers stored in the server_series collection against the timestamps
    """
    def graph_queue_length_by_server(self, ax):
        for server_id, server_data in self.data_collector.server_series.items():
            timestamps = server_data['utilization']['timestamp']
            queue_lengths = server_data['utilization']['queue_length']
            ax.plot(timestamps, queue_lengths, label=server_id, linewidth=2)

        ax.set_title('Queue Length by Server Over Time', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Queue Length')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

    """
    Plots the queue utilizations for servers stored in the server_series collection against the timestamps
    """
    def graph_queue_utilization_by_server(self, ax):
        for server_id, server_data in self.data_collector.server_series.items():
            timestamp = server_data['utilization']['timestamp']
            queue_util = [util * 100 for util in server_data['utilization']['queue_utilization']]
            ax.plot(timestamp, queue_util, label=server_id, linewidth=2)

        ax.set_title('Queue Utilization by Server Over Time', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Queue Utilization (%)')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

    """
    Plots the CPU utilizations for servers stored in the server_series collection against the timestamps
    """
    def graph_cpu_utilization_by_server(self, ax):
        for server_id, server_data in self.data_collector.server_series.items():
            timestamp = server_data['utilization']['timestamp']
            cpu_util = [util * 100 for util in server_data['utilization']['cpu_utilization']]
            ax.plot(timestamp, cpu_util, label=server_id, linewidth=2)

        ax.set_title('CPU Utilization by Server Over Time', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('CPU Utilization (%)')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

    """
    Plots the traffic generation rates in the simulation_series collection against the timestamps
    """
    def graph_traffic_generation_rates(self, ax):
        times = self.data_collector.simulation_series['timestamp']

        # Calculate generation rates
        legit_rates = []
        malicious_rates = []

        for i in range(1, len(times)):
            time_diff = times[i] - times[i - 1]

            # Legitimate generation rate
            legit_sent_diff = (self.data_collector.legitimate_network_series['requests_sent'][i] -
                               self.data_collector.legitimate_network_series['requests_sent'][i - 1])
            legit_rates.append(legit_sent_diff / time_diff if time_diff > 0 else 0)

            # Malicious generation rate
            malicious_sent_diff = (self.data_collector.botnet_series['requests_sent'][i] -
                                   self.data_collector.botnet_series['requests_sent'][i - 1])
            malicious_rates.append(malicious_sent_diff / time_diff if time_diff > 0 else 0)

        ax.plot(times[1:], legit_rates, label='Legitimate Generation Rate', linewidth=2, color='blue')
        ax.plot(times[1:], malicious_rates, label='Malicious Generation Rate', linewidth=2, color='red')
        ax.set_title('Traffic Generation Rates: Legitimate vs Malicious', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Generation Rate (requests/sec)')
        ax.legend()
        ax.grid(True, alpha=0.3)

    """
    Plot the success rate of legitimate and malicious traffic against the timestamps in the simulation series
    """
    def graph_traffic_success_rates(self, ax):
        times = self.data_collector.simulation_series['timestamp']

        legit_success_rates = []
        malicious_success_rates = []

        for i in range(len(times)):
            # Legitimate success rate
            legit_sent = self.data_collector.legitimate_network_series['requests_sent'][i]
            legit_success = self.data_collector.legitimate_network_series['successful_response'][i]
            legit_rate = (legit_success / legit_sent * 100) if legit_sent > 0 else 0
            legit_success_rates.append(legit_rate)

            # Malicious success rate
            malicious_sent = self.data_collector.botnet_series['requests_sent'][i]
            malicious_success = self.data_collector.botnet_series['successful_response'][i]
            malicious_rate = (malicious_success / malicious_sent * 100) if malicious_sent > 0 else 0
            malicious_success_rates.append(malicious_rate)

        ax.plot(times, legit_success_rates, label='Legitimate Success Rate', linewidth=2, color='blue')
        ax.plot(times, malicious_success_rates, label='Malicious Success Rate', linewidth=2, color='red')
        ax.set_title('Success Rates: Legitimate vs Malicious Traffic', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Success Rate (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)

    """
    Plot the server health scores for servers in the server_series collection against the timestamps
    """
    def graph_server_health_by_server(self, ax):
        for server_id, server_data in self.data_collector.server_series.items():
            timestamp = server_data['utilization']['timestamp']
            health_scores = server_data['utilization']['health_score']
            ax.plot(timestamp, health_scores, label=server_id, linewidth=2)

        ax.set_title('Server Health by Server Over Time', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Health Score')
        ax.set_ylim(0, 1)  # Health score range
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

    #Helper method to help visualize plot data
    def hover(self, event, fig):
        if event.inaxes:
            ax = event.inaxes
            for line in ax.get_lines():
                if line.contains(event)[0]:
                    x, y = line.get_data()
                    idx = min(range(len(x)), key=lambda i: abs(x[i] - event.xdata))
                    # Show value in title
                    original = ax.get_title().split('|')[0].strip()
                    ax.set_title(f"{original} | {line.get_label()}: {y[idx]:.1f}")
                    fig.canvas.draw_idle()
                    return
            # Reset if not hovering
            original = ax.get_title().split('|')[0].strip()
            ax.set_title(original)
            fig.canvas.draw_idle()