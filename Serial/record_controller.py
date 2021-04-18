import threading

from DB.dao import SQLiteDAO
from Serial.callback import RecordControllerCallback
from Serial.serial_listener import SerialListener
from Serial.serial_message import SerialMessage, build_message, MessageType as Mt
from DB.model import Session, Temperature, Action


class RecordController:
    def __init__(self, serial_listener: SerialListener, dao: SQLiteDAO, callback: RecordControllerCallback):
        self.serial_listener = serial_listener
        self.dao = dao  # Type SQLiteDAO
        self.queue = serial_listener.queue
        self.callback = callback

        self._need_to_record = False
        self._start_queue_listening_thread()

        self.current_session = None
        self.set_current_session_as_new()

        self.message_handlers = {
            Mt.ERROR_MESSAGE: self._handle_error_message,
            Mt.MODE_MESSAGE: self._handle_mode_message,
            Mt.MAINTAINING_TEMP_MESSAGE: self._handle_maintaining_temp_message,
            Mt.TEMPERATURE_MESSAGE: self._handle_temperature_message,
            Mt.TURN_ON_OFF_MESSAGE: self._handle_turn_on_off_message,
            Mt.SIMPLE_MESSAGE: self._handle_simple_message,
        }

    def set_current_session_as_new(self):
        self.current_session = Session()
        self.current_session.id = None
        self.current_session.maintaining_temperature = 0

    def is_recording(self):
        return self._need_to_record

    def start_listening(self):
        self.serial_listener.start_listening()

    def stop_listening(self):
        self.serial_listener.stop_listening()
        self._need_to_record = False

    def start_recording(self):
        self.current_session = self.dao.create_session(self.current_session)
        self._need_to_record = True

    def stop_recording(self):
        self._need_to_record = False
        self.set_current_session_as_new()

    def _start_queue_listening_thread(self):
        listen_thread = threading.Thread(target=self._listen, daemon=True)
        listen_thread.start()

    def _listen(self):
        while True:
            message = self.queue.get(block=True)
            self._handle_message(message)

    def _handle_message(self, raw_message):
        message = build_message(raw_message)

        if message.type in self.message_handlers:
            self.message_handlers[message.type](message)

        #self.callback.on_receive_message(message)

    def _handle_error_message(self, message: SerialMessage):
        self.callback.on_error()
        self.stop_recording()

    def _handle_mode_message(self, message: SerialMessage):
        self.current_session.mod_name = message.text
        self.callback.on_receive_message(message.text)

    def _handle_maintaining_temp_message(self, message: SerialMessage):
        self.current_session.maintaining_temperature = float(message.text) / 100
        self.callback.on_receive_message(str(message))

    def _handle_temperature_message(self, message: SerialMessage):
        temp = Temperature.from_serial_message(message)
        self.callback.on_receive_temperature(temp)

        if self.is_recording() and self.current_session.id is not None:
            temp.session_id = self.current_session.id
            self.dao.add_temperature(temp)

    def _handle_turn_on_off_message(self, message: SerialMessage):
        action = Action.from_serial_message(message)
        if message.text == 'ON':
            self.callback.on_receive_turn_on(action)
        elif message.text == 'OFF':
            self.callback.on_receive_turn_off(action)

        self.callback.on_receive_message(str(message))

        if self.is_recording():
            self.dao.add_action(action)

    def _handle_simple_message(self, message: SerialMessage):
        self.callback.on_receive_message(str(message))

