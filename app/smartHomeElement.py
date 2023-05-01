from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Tuple, List

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






class SolarPanel(SmartHomeElement):
    def __init__(self,
                 name: str,
                 energy_load: float,
                 running_time: timedelta,
                 running_cost: float,
                 time_window: List[datetime],
                 interruptible: bool,
                 area: float,
                 eta: float):
        # area (float): Total area of the photovoltaic panels in [m^2]
        # eta (float): Photoelectric conversion efficiency of solar panels [{0}].
        super().__init__(name,
                         energy_load,
                         running_time,
                         running_cost,
                         time_window,
                         interruptible)
        self.area = area
        self.eta = eta

    def compute_pv_output(self, Ij: float, Tj: float) -> float:
        """
        Computes the power output of photovoltaic panels using the regression model based on ref:
        [1] ]Muzathik, A.M., 2014. Photovoltaic modules operating temperature estimation using a simple correlation. Int. J. Energy Eng. 4, 151.
        Args:
        - Ij (float): Total irradiance for the given weather conditions.
        - Tj (float): Average photovoltaic panels temperature in [C].

        Returns:
        - PVj (float): Power output of the photovoltaic panels.
        """
        return self.eta * self.area * Ij * (1 - 0.005 * (Tj + 25))


