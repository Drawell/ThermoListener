from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from queue import Queue

from DB.model import Temperature, Session
from Serial.callback import RecordControllerCallback
from metric_calculator import MetricCalculator
from .main_window_gui import Ui_MainWindow
from .graph_widget import GraphWidget
from Serial.serial_listener import SerialListener, MockSerialListener
from Serial.record_controller import RecordController
from DB.dao import SQLiteDAO
from .session_list_widget import SessionListWidget


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.serial_listener = SerialListener(Queue(maxsize=100))
        # self.serial_listener = MockSerialListener(Queue(maxsize=100))
        self.dao = SQLiteDAO()

        self.controller_callback = RecordControllerCallback()

        self.record_controller = RecordController(self.serial_listener, self.dao, self.controller_callback)
        self.metric_calculator = MetricCalculator()

        self.setupUi(self)
        self.setup_additional_ui()

        self.start_listening()

    def setup_additional_ui(self):
        self.graph_widget = GraphWidget()
        self.verticalLayout_3.addWidget(self.graph_widget)

        self.fill_port_combobox()
        self.session_widget = SessionListWidget(self, self.dao, self.show_session)
        self.verticalLayout.addWidget(self.session_widget)
        self.session_widget.refresh()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(lambda: self.graph_widget.update())
        self.timer.start()

        self.connect_ui_signals()

    def connect_ui_signals(self):
        self.refreshPortsPushButton.clicked.connect(self.fill_port_combobox)
        self.startRecordPushButton.clicked.connect(self._on_record_button_click)
        self.portListComboBox.currentTextChanged.connect(self.change_port)
        self.resetButton.clicked.connect(self.reset)
        self.saveButton.clicked.connect(self.graph_widget.export_to_file)

        self.controller_callback.on_error = self.receive_message
        self.controller_callback.on_receive_message = self.receive_message
        self.controller_callback.on_receive_temperature = self.receive_temperature
        self.controller_callback.on_receive_turn_on = self.graph_widget.add_action_turn_on
        self.controller_callback.on_receive_turn_off = self.graph_widget.add_action_turn_off
        self.controller_callback.on_receive_power = self.graph_widget.add_power
        self.controller_callback.on_exception = self.receive_exception
        self.controller_callback.on_add_new_session = self.session_widget.refresh

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
            self.startRecordPushButton.setText('Начать запись')
            self.record_controller.stop_recording()
        else:
            self.graph_widget.clear_data()
            self.metric_calculator.clear()
            self.startRecordPushButton.setText('Остановить запись')
            self.record_controller.start_recording()

    def reset(self):
        self.graph_widget.clear_data()
        self.metric_calculator.clear()
        self.portMessagesTextEdit.clear()
        if self.record_controller.is_stopped():
            self.isRecordingLabel.setText('Слушаем...')
            self.resetButton.setText('Очистить')
            self.record_controller.start_listening()

    def add_text_to_message_te(self, text: str):
        self.portMessagesTextEdit.append(text)
        self.portMessagesTextEdit.verticalScrollBar().setValue(
            self.portMessagesTextEdit.verticalScrollBar().maximum())

    def receive_message(self, message: str):
        self.add_text_to_message_te(message)

    def receive_temperature(self, temp: Temperature):
        self.graph_widget.set_maintaining_temp(self.record_controller.current_session.maintaining_temperature)
        self.graph_widget.add_temperature(temp)

        self.metric_calculator.add_temperature(temp)
        self.metric_calculator.maintaining_temperature = self.record_controller.current_session.maintaining_temperature
        self.print_metrics()

    def receive_exception(self, exception):
        print(exception)
        self.add_text_to_message_te(exception)

    def show_session(self, session: Session):
        self.graph_widget.clear_data()

        self.graph_widget.set_maintaining_temp(session.maintaining_temperature)
        self.metric_calculator.clear()
        self.metric_calculator.maintaining_temperature = session.maintaining_temperature

        self._load_temp_and_power(session, True)

        self.print_metrics()
        self.record_controller.stop_listening()
        self.resetButton.setText('Продолжить слушать')
        self.isRecordingLabel.setText('Смотрим...')

    def _load_temp_and_power(self, session, clip=False):
        min_temp = 30
        record_time = 60 * 7  # 5 7
        if clip:
            clip_timestamp = None
            for temp in session.temperatures:
                if clip_timestamp is not None:
                    if (temp.time - clip_timestamp).total_seconds() > record_time:
                        break

                if temp.temperature > min_temp:
                    self.graph_widget.add_temperature(temp)
                    self.metric_calculator.add_temperature(temp)

                    if clip_timestamp is None:
                        clip_timestamp = temp.time

            for power in session.powers:
                if power.time >= clip_timestamp and (power.time - clip_timestamp).total_seconds() <= record_time:
                    self.graph_widget.add_power(power)
        else:
            for temp in session.temperatures:
                self.graph_widget.add_temperature(temp)
                self.metric_calculator.add_temperature(temp)
            for power in session.powers:
                self.graph_widget.add_power(power)

    def print_metrics(self):
        max_overheat = self.metric_calculator.max_overheat
        self.labelMaxOverheat.setText('%.2f °C' % max_overheat if max_overheat else '-')

        deviation = self.metric_calculator.deviation
        self.labelDeviation.setText('%.2f' % deviation if deviation else '-')

        heat_time = self.metric_calculator.heat_time
        self.labelHeatTime.setText(str(heat_time) + ' сек.' if heat_time else '-')
