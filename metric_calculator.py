from DB.model import Temperature


class MetricCalculator:
    def __init__(self):
        self.temperatures = []
        self.start_temperature = 30
        self.maintaining_temperature = 60

        self.max_overheat = None
        self.deviation = None
        self.record_count = 0
        self.temp_dif_sum = 0
        self.heat_time = None
        self.near_heating_time = None
        self.start_temperature_timestamp = None

    def clear(self):
        self.temperatures = []
        self.max_overheat = None
        self.deviation = None
        self.record_count = 0
        self.temp_dif_sum = 0
        self.heat_time = None
        self.near_heating_time = None
        self.start_temperature_timestamp = None

    def add_temperature(self, temp: Temperature):
        self.temperatures.append(temp)
        self._calc_overheat(temp)
        self._calc_deviation(temp)
        self._calc_heating_time(temp)

    def _calc_overheat(self, temp: Temperature):
        if temp.temperature >= self.maintaining_temperature:
            overheat = temp.temperature - self.maintaining_temperature
            if self.max_overheat is not None:
                self.max_overheat = max(self.max_overheat, overheat)
            else:
                self.max_overheat = overheat

    def _calc_deviation(self, temp: Temperature):
        if self.near_heating_time is not None:
            dif = (temp.temperature - self.maintaining_temperature) * (temp.temperature - self.maintaining_temperature)
            self.temp_dif_sum += dif
            self.record_count += 1

            self.deviation = self.temp_dif_sum / self.record_count

    def _calc_heating_time(self, temp: Temperature):
        if temp.temperature >= self.start_temperature and self.start_temperature_timestamp is None:
            self.start_temperature_timestamp = temp.time

        if self.near_heating_time is None \
                and temp.temperature >= self.maintaining_temperature - 1 \
                and self.start_temperature_timestamp is not None:
            self.near_heating_time = temp.time - self.start_temperature_timestamp
            self.near_heating_time = int(self.near_heating_time.total_seconds())

        if self.heat_time is None \
                and temp.temperature >= self.maintaining_temperature \
                and self.start_temperature_timestamp is not None:
            self.heat_time = temp.time - self.start_temperature_timestamp
            self.heat_time = int(self.heat_time.total_seconds())
