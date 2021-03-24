import os.path
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QDockWidget, QAction, QFileDialog, QLineEdit, QLabel
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon

from .main_window_gui import Ui_MainWindow
from serial_listener import SerialListener


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.ser = SerialListener()
        self.setupUi(self)
        self.setup_additional_ui()

        self.start_listening()

    def setup_additional_ui(self):
        self.connect_ui_signals()
        self.fill_port_combobox()

    def connect_ui_signals(self):
        self.refreshPortsPushButton.clicked.connect(self.fill_port_combobox)
        self.portListComboBox.currentTextChanged.connect(self.change_port)

    def change_port(self, port_name):
        self.ser.stop_listening()
        self.ser.choose_port(port_name)
        self.start_listening()

    def fill_port_combobox(self):
        self.portListComboBox.clear()
        ports = self.ser.get_all_com_ports()
        self.portListComboBox.insertItems(0, ports)

    def start_listening(self):
        try:
            self.ser.start_listening(self.print_to_textbox)
        except Exception as e:
            print(str(e))

    def print_to_textbox(self, message: str):
        self.portMessagesTextEdit.append(message + '\n')
