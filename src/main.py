from SimulationExecutive import SimulationExecutive
from utils.ConfigValidator import validate_config

if __name__ == "__main__":
    if not validate_config():
        exit(1)
    simulation_executive = SimulationExecutive()
    simulation_executive.run_simulation()