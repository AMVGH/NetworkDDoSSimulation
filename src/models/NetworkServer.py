import simpy

from src.models.Request import Request
from src.config import (
    SERVER_TIMEOUT,
    REQUEST_TIMEOUT,
    INCREASED_UTILIZATION,
    HIGH_UTILIZATION,
    CRITICAL_UTILIZATION,
    CPU_UTILIZATION_HEALTH_WEIGHT,
    QUEUE_UTILIZATION_HEALTH_WEIGHT)

class NetworkServer:
    def __init__(self, env: simpy.Environment, server_id: str, processing_power: float, max_requests_concurrent: int, max_request_queue_len: int):
        self.env = env
        self.server_id = server_id
        self.processing_power = processing_power
        self.max_requests_concurrent = max_requests_concurrent
        self.max_request_queue_len = max_request_queue_len

        #Fields for ongoing health and utilization
        self.current_requests_concurrent = 0
        self.cpu_utilization = 0.0 #(Range 0.0 - 1.0)
        self.process_queue_utilization = 0.0 #(Range 0.0 - 1.0)
        self.queue_length = 0
        self.server_health = 0 # Extrapolation of CPU and Queue utilization
        self.is_server_online = True
        self.current_request = None

        #Utilization thresholds to help guide logic to model server degradation impacting performance
        self.increased_utilization = INCREASED_UTILIZATION
        self.high_utilization = HIGH_UTILIZATION
        self.critical_utilization = CRITICAL_UTILIZATION

        #Request Queue and Worker Processes
        self.request_process_worker = simpy.Resource(env, self.max_requests_concurrent)
        self.request_queue = simpy.Store(env)

        #Request Tracking Metrics
        self.total_requests_processed = 0
        self.failed_requests = 0
        self.dropped_requests_server_offline = 0
        self.dropped_requests_queue_full = 0
        self.dropped_requests_timeout = 0

        #Start Process
        self.process_requests = env.process(self.process_request())

    def calculate_processing_time(self, request: Request):
        """
        Calculates the processing time for a request based on the load size and the current CPU utilization.
        """
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

    def update_cpu_utilization(self):
        self.cpu_utilization = self.current_requests_concurrent / self.max_requests_concurrent

    def update_queue_utilization(self):
        self.process_queue_utilization = self.queue_length / self.max_request_queue_len

    def update_server_health(self):
        self.server_health = (CPU_UTILIZATION_HEALTH_WEIGHT * self.cpu_utilization
                              + QUEUE_UTILIZATION_HEALTH_WEIGHT * self.process_queue_utilization)

    def shutdown_server(self):
        """
        Servers should be coming online and offline, where if the queue is full it is set offline and set online once timeout has elapsed.
        """
        self.is_server_online = False
        yield self.env.timeout(SERVER_TIMEOUT)
        print(f"[{self.env.now}] Server is back online.")
        self.is_server_online = True

    def receive_request(self, request: Request):
        if request.is_routed:
            return False

        if len(self.request_queue.items) >= self.max_request_queue_len:
            if self.is_server_online:
                print(f"[{self.env.now}] Server is shutting down.")
                self.env.process(self.shutdown_server())
            self.dropped_requests_queue_full += 1
            print(
                f"[{self.env.now}] Request {request.request_id} (Origin {request.source_id}) has hit the server while at max queue length. "
                f"Server has been shut down for {SERVER_TIMEOUT} time units. "
                f"Dropped requests (QF): {self.dropped_requests_queue_full}")
            return False

        if not self.is_server_online:
            self.dropped_requests_server_offline += 1
            print(f"[{self.env.now}] Request {request.request_id} (Origin {request.source_id}) has hit the server while the server is offline and has been dropped. "
                  f"Dropped requests (SOL): {self.dropped_requests_server_offline}")
            return False


        #Request is stamped with its arrival time and is marked as routed
        request.set_arrival_time(self.env.now)
        request.mark_routed()

        self.request_queue.put(request)
        self.queue_length = len(self.request_queue.items)
        self.update_queue_utilization()
        self.update_server_health()
        print(f"[{self.env.now}] Request {request.request_id} (Origin {request.source_id}) has successfully been added to process queue.")
        return True

    #TODO: Possibly return a request to the network router as a bucket where we can get a view of served and origin? - Can be scrapped
    def process_request(self):
        while True:
            #Take a request from the request queue and update the length of the queue
            request = yield self.request_queue.get()
            self.queue_length = len(self.request_queue.items)
            print(f"[{self.env.now}] Request {request.request_id} has been dequeued and awaiting process. Queue length now: {self.queue_length}")

            #Calculates how long the request has already waited and the remaining time until timeout
            request_wait_time = self.env.now - request.arrival_time
            remaining_request_wait_time = max(0, REQUEST_TIMEOUT - request_wait_time)

            #If the remaining time is <= 0 (exceeds REQUEST_TIMEOUT) the request is timed out and number of dropped requests is incremented
            if remaining_request_wait_time <= 0:
                self.dropped_requests_timeout += 1
                print(
                    f"[{self.env.now}] Request {request.request_id} DROPPED (timeout in queue). Queue length: {self.queue_length}")
                continue

            print(f"[{self.env.now}] Request {request.request_id} is currently dequeued. Waiting time: {request_wait_time}, Remaining timeout: {remaining_request_wait_time}")
            print(f"[{self.env.now}] Queue length: {self.queue_length}, CPU utilization: {self.cpu_utilization} (Should be 0)")

            request_worker_process = self.request_process_worker.request()
            request_timeout = self.env.timeout(remaining_request_wait_time)
            result = yield simpy.events.AnyOf(self.env, [request_worker_process, request_timeout])

            if request_worker_process in result:
                with request_worker_process:
                    # Increment concurrent requests and update CPU utilization
                    self.current_requests_concurrent += 1
                    self.update_cpu_utilization()

                    #TODO: Verify utilization metrics are being updated properly seems as though being read wrong - * 100 to get log %
                    print(f"[{self.env.now}] Request {request.request_id} has received a worker process and has STARTED processing. "
                          f"Concurrent requests: {self.current_requests_concurrent}, CPU utilization: {self.cpu_utilization}, Queue length: {self.queue_length}")

                    request_process_time = self.calculate_processing_time(request)
                    yield self.env.timeout(request_process_time)

                    print(f"[{self.env.now}] Request {request.request_id} FINISHED processing. "
                          f"Processing time: {request_process_time}, CPU utilization: {self.cpu_utilization}, Queue length: {self.queue_length}")

                    # Decrement concurrent requests and update CPU utilization
                    self.current_requests_concurrent -= 1
                    self.update_cpu_utilization()

                    print(f"[{self.env.now}] Working process FINISH. CPU utilization: {self.cpu_utilization} (Should be 0), Queue length: {self.queue_length}")

                    request.set_served_time(self.env.now)
                    request.set_is_served(True)
                    self.total_requests_processed += 1
            else:
                self.dropped_requests_timeout += 1
                print(
                    f"[{self.env.now}] Request {request.request_id} DROPPED (timeout waiting for worker). Queue length: {self.queue_length}, CPU utilization: {self.cpu_utilization:.2f}")