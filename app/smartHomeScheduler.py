from smartHomeElement import SmartHomeElement
from typing import List

class SmartHomeScheduler:
    def __init__(self,
                 elements: List[SmartHomeElement],
                 prices: List[float],
                 battery_capacity: float):
        self.elements = elements
        self.prices = prices
        self.battery_capacity = battery_capacity

    def schedule_day_ahead(self,
                           energy_demand: List[float],
                           energy_prices: List[float]) -> List[List[SmartHomeElement]]:
        """
        Returns a list of lists of SmartHomeElement objects scheduled for each hour of the day
        based on the estimated energy demand and day-ahead energy prices.
        """
        scheduled_elements = [[] for _ in range(24)]  # initialize empty list of lists

        # iterate over each hour of the day
        for hour in range(24):
            available_energy = energy_demand[hour]  # use estimated energy demand for the hour as available energy
            available_budget = energy_prices[hour] * available_energy  # calculate available budget based on day-ahead energy prices

            # sort elements by running cost and get schedulable elements for the hour
            schedulable_elements = sorted(self.elements, key=lambda x: x.running_cost)
            schedulable_elements = self._get_schedulable_elements(hour, schedulable_elements, available_energy, available_budget)

            # add scheduled elements for the hour to the list of scheduled elements
            scheduled_elements[hour] = schedulable_elements

        return scheduled_elements

    def optimize_schedule(self,
                          day_ahead_prices: List[float],
                          energy_demand: List[float]) -> List[SmartHomeElement]:

        scheduled_elements = self.schedule_day_ahead(day_ahead_prices, energy_demand)
        for hour in range(len(day_ahead_prices)):
            if scheduled_elements[hour] is None:
                continue
            available_elements = [elem for elem in self.elements if elem.time_window[0] <= hour < elem.time_window[1] and elem.interruptible]
            if not available_elements:
                continue
            cheapest_element = min(available_elements, key=lambda elem: elem.get_price(hour))
            if cheapest_element.get_price(hour) < scheduled_elements[hour].get_price(hour):
                scheduled_elements[hour] = cheapest_element
        return scheduled_elements

    def _get_schedulable_elements(self,
                                  current_time: int,
                                  elements: List[SmartHomeElement],
                                  available_energy: float,
                                  available_budget: float) -> List[SmartHomeElement]:
        """
        Helper function to get the schedulable elements for the current hour based on their interruptibility,
        energy demand, running cost, and available energy and budget.
        """
        schedulable_elements = []
        for element in elements:
            # check if element can be scheduled at current time
            if current_time >= element.time_window[0] and current_time < element.time_window[1]:
                # check if element can be run without exceeding available energy and budget
                if element.interruptible or element.get_energy_demand() <= available_energy:
                    if element.get_price() <= available_budget:
                        schedulable_elements.append(element)
                        available_energy -= element.get_energy_demand()
                        available_budget -= element.get_price()

        return schedulable_elements

    def optimize_daily_price(self, pv_production: List[float], buy_prices: List[float]) -> List[float]:

        # Calculate the net energy demand by subtracting PV production from energy demand
        net_demand = []
        for i in range(24):
            demand = sum([elem.get_energy_demand(i) for elem in self.elements])
            pv_output = pv_production[i]
            net_demand.append(demand - pv_output)

        # Initialize battery state; full battery beginning of day
        battery_state = 1

        # Create a list to store the energy sources for each hour of the day
        # 0 = grid, 1 = battery, 2 = PV
        energy_sources = []

        # Calculate the energy sources for each hour of the day
        for i in range(24):
            demand = net_demand[i]
            buy_price = buy_prices[i]

            # Check if PV production is greater than demand
            if pv_production[i] >= demand:
                # PV production is greater than demand, so use excess to charge the battery
                if battery_state < self.battery_capacity:
                    energy_sources.append(1)
                    battery_state = min(battery_state + (pv_production[i] - demand), self.battery_capacity)
                else:
                    energy_sources.append(0)
            else:
                # PV production is less than demand
                remaining_demand = demand - pv_production[i]
                # Check if the battery has enough energy to supply the remaining demand
                if battery_state >= remaining_demand:
                    # Battery has enough energy, so use it to supply the remaining demand
                    energy_sources.append(1)
                    battery_state = battery_state - remaining_demand
                else:
                    # Battery doesn't have enough energy, so buy from the grid
                    energy_sources.append(0)

        # Calculate the total cost of energy for the day
        total_cost = sum([energy_sources[i] * buy_prices[i] for i in range(24)])

        return energy_sources, total_cost


