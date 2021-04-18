from random import randint

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow

from queue import Queue

from DB.model import Temperature
from Serial.callback import RecordControllerCallback
from Serial.serial_message import SerialMessage, MessageType
from .main_window_gui import Ui_MainWindow
from .graph_widget import GraphWidget
from Serial.serial_listener import SerialListener, MockSerialListener
from Serial.record_controller import RecordController
from DB.dao import SQLiteDAO


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__(None)
        #self.serial_listener = SerialListener(Queue(maxsize=100))
        self.serial_listener = MockSerialListener(Queue(maxsize=100))
        self.dao = SQLiteDAO()

        self.controller_callback = RecordControllerCallback()

        self.record_controller = RecordController(self.serial_listener, self.dao, self.controller_callback)

        self.setupUi(self)
        self.setup_additional_ui()

        self.start_listening()

    def setup_additional_ui(self):
        self.graph_widget = GraphWidget()
        self.verticalLayout_3.addWidget(self.graph_widget)

        self.connect_ui_signals()
        self.fill_port_combobox()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(lambda: self.graph_widget.update())
        self.timer.start()

    def connect_ui_signals(self):
        self.refreshPortsPushButton.clicked.connect(self.fill_port_combobox)
        self.startRecordPushButton.clicked.connect(self._on_record_button_click)
        self.portListComboBox.currentTextChanged.connect(self.change_port)

        self.controller_callback.on_receive_message = self.receive_message
        self.controller_callback.on_receive_temperature = self.receive_temperature
        self.controller_callback.on_receive_turn_on = self.graph_widget.add_action_turn_on
        self.controller_callback.on_receive_turn_off = self.graph_widget.add_action_turn_off

    def closeEvent(self, event):
        if self.record_controller.is_recording():
            self.record_controller.stop_recording()
        event.accept()

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

    def _on_record_button_click(self):
        if self.record_controller.is_recording():
            self.startRecordPushButton.setText('Start recording')
            self.record_controller.stop_recording()
        else:
            self.graph_widget.clear_data()
            self.startRecordPushButton.setText('Stop recording')
            self.record_controller.start_recording()

    def add_text_to_message_te(self, text: str):
        self.portMessagesTextEdit.append(text)
        self.portMessagesTextEdit.verticalScrollBar().setValue(
            self.portMessagesTextEdit.verticalScrollBar().maximum())

    def receive_message(self, message: SerialMessage):
        self.add_text_to_message_te(str(message))

    def receive_temperature(self, temp: Temperature):
        self.add_text_to_message_te(temp.time.strftime('[%H:%M:%S:%f]') + f'Temperature: {temp.temperature}')
        self.graph_widget.set_maintaining_temp(self.record_controller.current_session.maintaining_temperature)
        self.graph_widget.add_temperature(temp)




