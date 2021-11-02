import threading
from functools import wraps

from DB.dao import SQLiteDAO
from Serial.callback import RecordControllerCallback
from Serial.serial_listener import SerialListener
from Serial.serial_message import SerialMessage, build_message, MessageType as Mt
from DB.model import Session, Temperature, Action, Power


def serial_record_message_handler(item_class):
    def _wrapper(f):
        @wraps(f)
        def inner(self, serial_message):
            try:
                item = item_class.from_serial_message(serial_message)
                f(self, item)

                if self.is_recording() and self.current_session.id is not None:
                    item.session_id = self.current_session.id
                    self.dao.add_entry(item)

            except Exception as ex:
                self.handle_exception(str(ex))
        return inner

    return _wrapper


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
            Mt.POWER_MESSAGE: self._handle_power_message,
            Mt.ACTION_MESSAGE: self._handle_turn_on_off_message,
            Mt.SIMPLE_MESSAGE: self._handle_simple_message,
        }

    def set_current_session_as_new(self):
        self.current_session = Session()
        self.current_session.id = None
        self.current_session.maintaining_temperature = 0

    def is_recording(self):
        return self._need_to_record

    def start_listening(self):
        if self.serial_listener.is_stopped():
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
        if message is None:
            return

        if message.type in self.message_handlers:
            self.message_handlers[message.type](message)

        # self.callback.on_receive_message(message)

    def _handle_error_message(self, message: SerialMessage):
        self.callback.on_error(str(message))
        self.stop_recording()

    def _handle_mode_message(self, message: SerialMessage):
        self.current_session.mod_name = message.text
        self.callback.on_receive_message(str(message))

    def _handle_maintaining_temp_message(self, message: SerialMessage):
        self.current_session.maintaining_temperature = float(message.text) / 100
        self.callback.on_receive_message(str(message))

    @serial_record_message_handler(Temperature)
    def _handle_temperature_message(self, temp: Temperature):
        self.callback.on_receive_temperature(temp)
        self.callback.on_receive_message(str(temp))

    @serial_record_message_handler(Action)
    def _handle_turn_on_off_message(self, action):
        if action.text == 'Turn On':
            self.callback.on_receive_turn_on(action)
        elif action.text == 'Turn Off':
            self.callback.on_receive_turn_off(action)

        self.callback.on_receive_message(str(action))

    @serial_record_message_handler(Power)
    def _handle_power_message(self, power: Power):
        self.callback.on_receive_message(str(power))
        self.callback.on_receive_power(power)

    def _handle_simple_message(self, message: SerialMessage):
        self.callback.on_receive_message(str(message))

    def handle_exception(self, exception):
        self.callback.on_exception(exception)
