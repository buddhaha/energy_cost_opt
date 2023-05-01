from abc import ABC, abstractmethod
from typing import Tuple

class SmartHomeElement(ABC):
    def __init__(self, name: str,
                 energy_load: float,
                 running_time: int,
                 running_cost: float,
                 priority: float,
                 time_window: Tuple[int, int],
                 interruptible: bool):
        self.name = name
        self.energy_load = energy_load  # in kW
        self.running_time = running_time  # in h
        self.running_cost = running_cost  # in e/kWh
        self.priority = priority # 1 to 10
        self.time_window = time_window  # start and end times in 24-hour format
        self.interruptible = interruptible

    @abstractmethod
    def run(self):
        pass

    def get_energy_demand(self) -> float:
        """
        Returns the energy demand of the smart home element for a single run in kWh.
        """
        return self.energy_load * self.running_time

    def get_price(self) -> float:
        """
        Returns the cost of running the smart home element for a single run in e.
        """
        return self.get_energy_demand() * self.running_cost




