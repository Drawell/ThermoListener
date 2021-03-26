import os.path
import time
from random import randint

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QDockWidget, QAction, QFileDialog, QLineEdit, QLabel
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

from queue import Queue

from serial_message import SerialMessage, MessageType
from .main_window_gui import Ui_MainWindow
from serial_listener import SerialListener
from record_controller import RecordController


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.serial_listener = SerialListener(Queue(maxsize=100))
        self.record_controller = RecordController(self.serial_listener, self.receive_message)

        self.setupUi(self)
        self.setup_additional_ui()

        self.start_listening()

        self.graphWidget = pg.PlotWidget()
        self.verticalLayout_2.addWidget(self.graphWidget)

        self.x = [] # list(range(100))  # 100 time points
        self.y = [] #[randint(0,100) for _ in range(100)]  # 100 data points

        self.graphWidget.setBackground('w')

        self.data_line = self.graphWidget.plot(self.x, self.y)
        # ... init continued ...
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        #self.timer.start()

    def update_plot_data(self):
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        self.y.append(randint(0, 100))  # Add a new random value.

        self.data_line.setData(self.x, self.y)  # Update the data.

    def setup_additional_ui(self):
        self.connect_ui_signals()
        self.fill_port_combobox()

    def connect_ui_signals(self):
        self.refreshPortsPushButton.clicked.connect(self.fill_port_combobox)
        self.portListComboBox.currentTextChanged.connect(self.change_port)

    def change_port(self, port_name):
        self.record_controller.stop_listening()
        self.serial_listener.choose_port(port_name)
        self.start_listening()

    def fill_port_combobox(self):
        self.portListComboBox.clear()
        ports = SerialListener.get_all_com_ports()
        self.portListComboBox.insertItems(0, ports)

    def start_listening(self):
        try:
            self.record_controller.start_listening()
        except Exception as e:
            print(str(e))

    def receive_message(self, message: SerialMessage):
        self.portMessagesTextEdit.append(str(message))
        if message.type == MessageType.TEMPERATURE_MESSAGE:
            t = int(message.text[2:])
            self.x.append(message.time.minute * 60 + message.time.second)  # Add a new value 1 higher than the last.

            if len(self.y) > 50:
                self.x = self.x[1:]  # Remove the first y element.
                self.y = self.y[1:]  # Remove the first

            self.y.append(t)  # Add a new random value.

            self.data_line.setData(self.x, self.y)  # Update the data.

