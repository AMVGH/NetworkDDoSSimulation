import simpy
import random as random

from src.models.Request import Request
from src.config import (
    SERVER_TIMEOUT,
    REQUEST_TIMEOUT,
    INCREASED_UTILIZATION,
    HIGH_UTILIZATION,
    CRITICAL_UTILIZATION,
    CPU_UTILIZATION_HEALTH_WEIGHT,
    QUEUE_UTILIZATION_HEALTH_WEIGHT,
    OFFLINE_CLEAR_THRESHOLD,
    HIGH_UTILIZATION_REJECTION_RATE)

class NetworkServer:
    def __init__(self, env: simpy.Environment, server_id: str, processing_power: float, max_requests_concurrent: int, max_request_queue_len: int):
        self.env = env
        self.server_id = server_id
        self.processing_power = processing_power
        self.max_requests_concurrent = max_requests_concurrent
        self.max_request_queue_len = max_request_queue_len

        #Fields for ongoing health and utilization
        self.cpu_utilization = 0.0 #(Range 0.0 - 1.0)
        self.process_queue_utilization = 0.0 #(Range 0.0 - 1.0)
        self.server_health = 0 #Extrapolation of CPU and Queue Utilization
        self.is_server_online = True

        #Utilization thresholds to help guide logic to model server degradation impacting performance
        self.increased_utilization = INCREASED_UTILIZATION
        self.high_utilization = HIGH_UTILIZATION
        self.critical_utilization = CRITICAL_UTILIZATION

        #Request Queue and Worker Processes
        self.request_process_worker = simpy.Resource(env, self.max_requests_concurrent)
        self.request_queue = simpy.Store(env)

        #Request Tracking Metrics
        self.total_requests_received = 0
        self.total_requests_processed = 0
        self.dropped_requests_queue_full = 0
        self.dropped_requests_process_timeout = 0
        self.dropped_requests_high_load = 0

        #Start Processes
        for i in range(self.max_requests_concurrent):
            env.process(self.process_request())

    """
    Calculates the processing time for a given request based on the load size and the current CPU utilization.
    """
    def calculate_processing_time(self, request: Request):
        process_time = request.load_size / self.processing_power
        if self.cpu_utilization > self.increased_utilization:
            increased_utilization_over = (self.cpu_utilization - self.increased_utilization)
            if self.cpu_utilization < self.high_utilization:
                server_degrade_factor = 1.0 + (increased_utilization_over * 2.0)
            else:
                high_utilization_over = (self.cpu_utilization - self.high_utilization)
                server_degrade_factor = 1.0 + (increased_utilization_over * 3.0) + (high_utilization_over * 5.0)
            process_time *= server_degrade_factor
        return process_time

    """
    Updates the CPU utilization of the server by dividing the number of concurrent requests consumed
    by request workers by the maximum number of concurrent requests; Assigns this value to cpu_utilization.
    """
    def update_cpu_utilization(self):
        concurrent_requests = self.request_process_worker.count
        self.cpu_utilization = concurrent_requests / self.max_requests_concurrent

    """
    Updates the queue utilization of the server by dividing the length of the current request queue 
    by the maximum length of the request queue; Assigns this value to process_queue_utilization.
    """
    def update_queue_utilization(self):
        current_queue_length = len(self.request_queue.items)
        self.process_queue_utilization = current_queue_length / self.max_request_queue_len

    """
    Updates the health of the server by multiplying both CPU utilization and queue utilization by
    their respective weights. Adds these values together and assigns them to server health. Server health is
    designed to be an extrapolation of both the CPU and queue utilization to see how overwhelmed a server 
    currently is.
    """
    def update_server_health(self):
        self.server_health = 1.0 - (CPU_UTILIZATION_HEALTH_WEIGHT * self.cpu_utilization
                              + QUEUE_UTILIZATION_HEALTH_WEIGHT * self.process_queue_utilization)
        self.server_health = max(0.0, self.server_health)

    """
    Facilitates the server coming online and offline. There is logic for timeout variance in
    order to avoid all X servers going down/up at the exact same moment. Furthermore, there is logic 
    to prevent servers coming back online prior to adequate queue depletion.
    """
    def shutdown_server(self):
        #Adding time variance to the base timeout period to prevent flat timeout across network. (Servers now will come back online at varied time units instead
        # of X servers coming back all at once).
        server_timeout_added_variance = SERVER_TIMEOUT + random.uniform(-0.5, 2.0)
        yield self.env.timeout(server_timeout_added_variance)

        #Server will continue to be offline if queue length exceeds the clear threshold. (Prevents the issue of server coming back online at full queue utilization)
        while len(self.request_queue.items) > self.max_request_queue_len * OFFLINE_CLEAR_THRESHOLD:
            yield self.env.timeout(1) #Timeout for a single time unit

        self.is_server_online = True

        #Prevents the issue of a newly restarted server being overwhelmed with traffic again. By setting CPU utilization to 0.1 the network routing
        #algorithm should target servers with better health scores. The proper CPU utilization will be written on the next incoming request
        self.cpu_utilization = 0.1
        self.process_queue_utilization = len(self.request_queue.items) / self.max_request_queue_len
        self.update_server_health()
        print(
            f"[{self.env.now:.5f}] Server {self.server_id} back online. Queue: {len(self.request_queue.items)}/{self.max_request_queue_len}")

    """
    Method designed to receive a request and add it to the processing queue. 
    """
    def receive_request(self, request: Request):
        #Return false if the incoming request has been seen by another server
        if request.is_routed:
            return False

        self.total_requests_received += 1

        #If the queue is full trigger immediate shutdown and drop the request
        current_queue_length = len(self.request_queue.items)
        if current_queue_length >= self.max_request_queue_len:
            self.is_server_online = False
            print(f"[{self.env.now:.5f}] Server {self.server_id} QUEUE FULL, SHUTTING DOWN.")
            self.env.process(self.shutdown_server())
            self.dropped_requests_queue_full += 1
            print(
                f"[{self.env.now:.5f}] Request {request.request_id} (Origin {request.source_id}) DROPPED due to QUEUE FULL ({current_queue_length}/{self.max_request_queue_len}).")
            return False

        #If the queue is not full but is at high utilization, reject requests based on the rejection rate
        queue_capacity_threshold = HIGH_UTILIZATION * self.max_request_queue_len
        if current_queue_length > queue_capacity_threshold:
            if random.random() < HIGH_UTILIZATION_REJECTION_RATE:
                self.dropped_requests_high_load += 1
                print(f"[{self.env.now:.5f}] Request {request.request_id} (Origin {request.source_id}) DROPPED due to HIGH SERVER LOAD ({current_queue_length}/{self.max_request_queue_len}).")
                return False

        #Request is stamped with an arrival time, marked as routed, and added to the request queue
        request.set_arrival_time(self.env.now)
        request.mark_routed()
        request.set_seen_by(self.server_id)
        self.request_queue.put(request)

        #Since the request queue has been updated, the queue utilization and health are updated
        self.update_queue_utilization()
        self.update_server_health()

        print(f"[{self.env.now:.5f}] Request {request.request_id} (Origin {request.source_id}) has been ADDED to queue. "
              f"(Server: {self.server_id}) "
              f"(QL: {len(self.request_queue.items)}/{self.max_request_queue_len}) "
              f"(Health: {self.server_health})")
        return True

    """
    Method designed to process a request, either serving the request or dropping it.
    """
    def process_request(self):
        while True:
            #Take a request from the request queue
            request = yield self.request_queue.get()

            #Update queue utilization and server health
            self.update_queue_utilization()
            self.update_server_health()

            print(f"[{self.env.now:.5f}] Request {request.request_id} (Origin {request.source_id}) has been DEQUEUED and awaiting process. Queue length now: {len(self.request_queue.items)} (Server: {self.server_id})")

            #Calculates how long the request has already waited and the remaining time until timeout
            request_wait_time = self.env.now - request.arrival_time
            remaining_request_wait_time = max(0, REQUEST_TIMEOUT - request_wait_time)

            #If the remaining time is <= 0 (exceeds REQUEST_TIMEOUT) the request is timed out and number of dropped requests is incremented
            if remaining_request_wait_time <= 0:
                self.dropped_requests_process_timeout += 1
                if hasattr(request, 'mark_failed'):
                    request.mark_failed('DROPPED (timeout in queue)')
                print(
                    f"[{self.env.now:.5f}] Request {request.request_id} (Origin {request.source_id}) DROPPED (timeout in queue). Queue length: {len(self.request_queue.items)}")
                continue

            print(f"[{self.env.now:.5f}] Request {request.request_id} (Origin {request.source_id}) is AWAITING PROCESS. Waiting time: {request_wait_time}, Remaining timeout: {remaining_request_wait_time}")
            print(f"[{self.env.now:.5f}] Queue length: {len(self.request_queue.items)}, CPU utilization: {self.cpu_utilization} (Server {self.server_id})")

            request_worker_process = self.request_process_worker.request()
            request_timeout = self.env.timeout(remaining_request_wait_time)
            result = yield simpy.events.AnyOf(self.env, [request_worker_process, request_timeout])

            if request_worker_process in result:
                with request_worker_process:
                    #Update CPU utilization and server health
                    self.update_cpu_utilization()
                    self.update_server_health()

                    print(
                        f"[{self.env.now:.5f}] Request {request.request_id} (Origin {request.source_id}) has received a worker process and has STARTED processing. "
                        f"Concurrent requests: {self.request_process_worker.count}, CPU utilization: {self.cpu_utilization} ({self.request_process_worker.count}/{self.max_requests_concurrent} workers active), Queue length: {len(self.request_queue.items)} (Server {self.server_id}).")

                    request_process_time = self.calculate_processing_time(request)
                    yield self.env.timeout(request_process_time)

                self.update_cpu_utilization()
                self.update_server_health()

                request.set_served_time(self.env.now)
                request.set_is_served(True)

                self.total_requests_processed += 1
                print(f"[{self.env.now:.5f}] Request {request.request_id} (Origin {request.source_id}) FINISHED processing. "
                      f"Processing time: {request_process_time}, CPU utilization: {self.cpu_utilization} ({self.request_process_worker.count}/{self.max_requests_concurrent} workers active), Queue length: {len(self.request_queue.items)} (Server {self.server_id}).")
            else:
                self.dropped_requests_process_timeout += 1
                self.update_cpu_utilization()
                self.update_server_health()

                if hasattr(request, 'mark_failed'):
                    request.mark_failed('DROPPED (timeout waiting for worker)')
                print(
                    f"[{self.env.now:.5f}] Request {request.request_id} (Origin {request.source_id}) DROPPED (timeout waiting for worker). Queue length: {len(self.request_queue.items)}, CPU utilization: {self.cpu_utilization:.2f} ({self.request_process_worker.count}/{self.max_requests_concurrent} workers active) (Server {self.server_id})")