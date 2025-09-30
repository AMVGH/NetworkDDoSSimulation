#TODO: Possibly expand in terms of data collection potential
class Request:
    def __init__(self, source_id: str, traffic_type: str, load_size: float):
        self.source_id = source_id
        self.traffic_type = traffic_type
        self.load_size = load_size
        self.request_id = None
        self.arrival_time = None
        self.served_time = None
        self.is_served = False
        self.is_routed = False

    def set_request_id(self, request_id: int):
        if self.request_id is not None:
            raise ValueError("Request ID already assigned")
        else: self.request_id = request_id

    def set_arrival_time(self, arrival_time):
        if self.arrival_time is not None:
            raise ValueError("Arrival time already assigned")
        else: self.arrival_time = arrival_time

    def set_served_time(self, served_time):
        if self.served_time is not None:
            raise ValueError("Served time already assigned")
        else: self.served_time = served_time

    def set_is_served(self, is_served):
        if self.is_served:
            raise ValueError("Request already served")
        else: self.is_served = is_served

    def mark_routed(self):
        if self.is_routed:
            raise ValueError("Request already routed")
        else: self.is_routed = True

