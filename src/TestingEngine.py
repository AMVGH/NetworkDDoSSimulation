import pytest
import simpy
from src.models.Request import Request
from src.utils.GenericEnums import TRAFFICTYPES

"""
Tests to ensure that object instantiation, core calculations, and other functionality is working as expected.
"""
def test_request_creation():
    def dummy_callback(request, success, failure_reason=None):
        pass

    request = Request(
        source_id="TEST_ENGINE",
        traffic_type=TRAFFICTYPES.LEGITIMATE.value,
        load_size=2.5,
        on_completion=dummy_callback
    )

    assert request.source_id == "TEST_ENGINE"
    assert request.load_size == 2.5
    assert request.is_routed == False

def test_request_setters():
    def dummy_callback(request, success, failure_reason=None):
        pass

    request = Request("TEST_ENGINE", TRAFFICTYPES.MALICIOUS.value, 1.0, dummy_callback)

    request.set_request_id(100)
    assert request.request_id == 100

    request.mark_routed()
    assert request.is_routed == True

def test_network_initialization():
    env = simpy.Environment()
    network = Network(env)

    assert network.incoming_request_count == 0
    assert len(network.network_servers) > 0

def test_network_router_initialization():
    mock_servers = [DummyClass() for i in range(3)]
    router = NetworkRouter(mock_servers)

    assert len(router.authorized_servers) == 3

def test_server_health_calculation():
    env = simpy.Environment()
    server = NetworkServer(env, "TEST_SERVER", 2.0, 5, 10)

    server.cpu_utilization = 0.6
    server.process_queue_utilization = 0.4
    server.update_server_health()

    # Health should be between 0 and 1
    assert server.server_health >= 0.0
    assert server.server_health <= 1.0

def test_processing_time_calculation():
    env = simpy.Environment()
    server = NetworkServer(env, "TEST_SERVER", 2.0, 5, 10)

    def dummy_callback(request, success, failure_reason=None):
        pass

    request = Request("TEST_ENGINE", TRAFFICTYPES.LEGITIMATE.value, 4.0, dummy_callback)

    process_time = server.calculate_processing_time(request)
    expected_time = 4.0 / 2.0

    assert process_time == expected_time

class DummyClass:
    def __init__(self):
        self.is_server_online = True
        self.server_health = 0.8

from src.models.Network import Network
from src.models.NetworkRouter import NetworkRouter
from src.models.NetworkServer import NetworkServer

if __name__ == "__main__":
    pytest.main([__file__, "-v"])