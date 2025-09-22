#expand

class Request:
    def __init__(self, request_id: str, source_id: str, traffic_type: str, load_size: float):
        self.request_id = request_id
        self.source_id = source_id
        self.traffic_type = traffic_type
        self.load_size = load_size
        self.arrival_time = None
        self.served_time = None