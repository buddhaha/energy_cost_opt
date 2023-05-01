from smartHomeElement import SmartHomeElement
from typing import List

class SmartHomeScheduler:
    def __init__(self, elements: List[SmartHomeElement]):
        self.elements = elements

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

