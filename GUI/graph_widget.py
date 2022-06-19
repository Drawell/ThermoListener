import math

from pyqtgraph import AxisItem, LegendItem
from datetime import datetime, timedelta
from time import mktime
import pyqtgraph as pg
import pyqtgraph.exporters as exporters
from PyQt5 import QtCore, QtGui

from DB.model import Temperature, Action, Power


class PlotAndData:
    def __init__(self, plot):
        self.plot = plot
        self.data = []
        self.timeline = []

    def clear(self):
        self.data.clear()
        self.timeline.clear()
        self.update()

    def add(self, value, time):
        self.data.append(value)
        self.timeline.append(time)

    def update(self):
        self.plot.setData(self.timeline, self.data)


class GraphWidget(pg.PlotWidget):
    def __init__(self):
        pg.PlotWidget.__init__(self)
        self.setBackground('w')
        self.start_time = None

        self.maintaining_temp = 0

        self.plotItem.addLegend(offset=(-30, 30),
                                labelTextSize='12pt',
                                labelTextColor='k')

        self.temp_plot = PlotAndData(self.plot(name='Текущая температура',
                                               pen=pg.mkPen(color=QtGui.QColor(255, 0, 0), width=3,
                                                            style=QtCore.Qt.SolidLine)))
        self.action_turn_on_plot = PlotAndData(self.plot(pen=None, symbol='o'))
        self.action_turn_off_plot = PlotAndData(self.plot(pen=None, symbol='x'))
        self.maintaining_temp_plot = PlotAndData(self.plot(name='Поддерживаемая температура',
                                                           pen=pg.mkPen(color=QtGui.QColor(50, 255, 50), width=1,
                                                                        style=QtCore.Qt.SolidLine)))

        self.power_plot = PlotAndData(self.plot(name='Мощность',
                                                pen=pg.mkPen(color=QtGui.QColor(50, 50, 255),
                                                             width=3,
                                                             style=QtCore.Qt.SolidLine)
                                                ))

        label_style = {'color': '#000', 'font-size': '12pt'}
        self.plotItem.setLabel('bottom', "Время (сек.)", '', **label_style)
        self.plotItem.setLabel('left', "Температура (°C) / Мощность (%)", **label_style)

        font = QtGui.QFont()
        font.setPixelSize(20)
        self.plotItem.getAxis("bottom").setStyle(tickFont=font)
        self.plotItem.getAxis("bottom").setTextPen('k')
        self.plotItem.getAxis("left").setStyle(tickFont=font, tickAlpha=1)
        self.plotItem.getAxis("left").setTextPen('k')

        self.plotItem.showGrid(x=True, y=True, alpha=0.2)

    def clear_data(self):
        self.start_time = None
        self.temp_plot.clear()
        self.action_turn_on_plot.clear()
        self.action_turn_off_plot.clear()
        self.power_plot.clear()

    def set_maintaining_temp(self, temp):
        self.maintaining_temp = temp

    def add_temperature(self, temp: Temperature):
        self.temp_plot.add(temp.temperature, self._get_timestamp(temp.time))
        self._update_maintaining_temp()

    def add_power(self, power: Power):
        self.power_plot.add(power.power, self._get_timestamp(power.time))
        self._update_maintaining_temp()

    def _get_timestamp(self, time: datetime):
        if self.start_time is None:
            self.start_time = time.timestamp()

        return int(time.timestamp() - self.start_time)

    def _update_maintaining_temp(self):
        if len(self.temp_plot.data) > 2:
            self.maintaining_temp_plot.data = [self.maintaining_temp, self.maintaining_temp]
            self.maintaining_temp_plot.timeline = [0, 0]

            self.maintaining_temp_plot.timeline[0] = self.temp_plot.timeline[0]
            self.maintaining_temp_plot.timeline[1] = self.temp_plot.timeline[
                len(self.temp_plot.timeline) - 1]

    def add_action_turn_on(self, action: Action):
        value = self.temp_plot.data[len(self.temp_plot.data) - 1]
        self.action_turn_on_plot.add(value, action.time.timestamp())

    def add_action_turn_off(self, action: Action):
        value = self.temp_plot.data[len(self.temp_plot.data) - 1]
        self.action_turn_off_plot.add(value, action.time.timestamp())

    def update(self):
        self.temp_plot.update()
        self.action_turn_on_plot.update()
        self.action_turn_off_plot.update()
        self.maintaining_temp_plot.update()
        self.power_plot.update()

    def export_to_file(self):
        now = datetime.now()
        name = now.strftime('%Y.%m.%d %H.%M.%S.%f')
        name = f"plots\\plot {name}.png"
        exporter = pg.exporters.ImageExporter(self.plotItem)
        exporter.parameters()['width'] = 1200
        exporter.export(name)
