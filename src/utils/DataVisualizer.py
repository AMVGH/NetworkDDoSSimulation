import matplotlib.pyplot as plot

from src.utils.DataCollector import DataCollector

#TODO: Check the other modules and refine the data being collected and plotted, update the plotting module and metric display
# - Metrics to Display:
#       - Server Response times
#       - Ability to serve legitimate network traffic (throughput)
#       - Performance degradation under load
#       - Legitimate request drop rate
#       - Request Response time
#       - Queue length
#       - Queue Utilization
#       - CPU Utilization
#       Response Metrics from Feedback:
#       - Request Generation Rate vs. Served Rate over time
#       - Per-server queue depths
#       - Drop Rate Patterns
#       - Legitimate vs Malicious Traffic Impact

class DataVisualizer:
    def __init__(self, data_collector):
        self.data = data_collector.time_series

    def plot_all_results(self):
        self.plot_cumulative_totals()
        self.plot_request_rates()
        plot.show()

    def plot_cumulative_totals(self):
        fig, ax = plot.subplots(figsize=(12, 6))

        time = self.data['time']

        ax.plot(time, self.data['total_generated'], 'b-', label='Total Generated', linewidth=2)
        ax.plot(time, self.data['total_served'], 'g-', label='Total Served', linewidth=2)

        ax.set_xlabel('Simulation Time')
        ax.set_ylabel('Cumulative Requests')
        ax.set_title('Cumulative Requests Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig

    def plot_request_rates(self):
        fig, (ax1, ax2) = plot.subplots(2, 1, figsize=(12, 8))

        time = self.data['time']

        # Calculate rates (requests per time unit)
        generated_rates = self._calculate_rates(self.data['total_generated'], time)
        served_rates = self._calculate_rates(self.data['total_served'], time)

        # Plot 1: Request rates
        ax1.plot(time, generated_rates, 'r-', label='Generation Rate', linewidth=2)
        ax1.plot(time, served_rates, 'g-', label='Service Rate', linewidth=2)
        ax1.set_ylabel('Requests per Time Unit')
        ax1.set_title('Request Generation vs Service Rates')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Drop rates
        queue_full_rates = self._calculate_rates(self.data['total_drops_queue_full'], time)
        timeout_rates = self._calculate_rates(self.data['total_drops_timeout'], time)
        high_load_rates = self._calculate_rates(self.data['total_drops_high_load'], time)
        no_server_rates = self._calculate_rates(self.data['total_drops_no_server'], time)

        ax2.plot(time, queue_full_rates, 'r-', label='Queue Full Drops', linewidth=2)
        ax2.plot(time, timeout_rates, 'orange', label='Timeout Drops', linewidth=2)
        ax2.plot(time, high_load_rates, 'yellow', label='High Load Drops', linewidth=2)
        ax2.plot(time, no_server_rates, 'purple', label='No Server Drops', linewidth=2)
        ax2.set_xlabel('Simulation Time')
        ax2.set_ylabel('Drops per Time Unit')
        ax2.set_title('Drop Rates Over Time')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plot.tight_layout()
        return fig

    def _calculate_rates(self, cumulative_data, time_points):
        rates = [0]  # First point
        for i in range(1, len(cumulative_data)):
            time_diff = time_points[i] - time_points[i - 1]
            value_diff = cumulative_data[i] - cumulative_data[i - 1]
            rate = value_diff / time_diff if time_diff > 0 else 0
            rates.append(rate)
        return rates

