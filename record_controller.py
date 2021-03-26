import threading
from queue import Queue

from dao import SQLLiteDAO
from serial_listener import SerialListener
from serial_message import SerialMessage, build_message


class RecordController:
    def __init__(self, serial_listener: SerialListener, on_receive_message):
        self.serial_listener = serial_listener
        self.queue = serial_listener.queue
        self.on_receive_message = on_receive_message

        self._need_to_record = False
        self._start_queue_listening_thread()

    def is_recording(self):
        return self._need_to_record

    def start_listening(self):
        self.serial_listener.start_listening()

    def stop_listening(self):
        self.serial_listener.stop_listening()
        self._need_to_record = False

    def start_recording(self):
        self._need_to_record = True

    def stop_recording(self):
        self._need_to_record = False

    def _start_queue_listening_thread(self):
        listen_thread = threading.Thread(target=self._listen,  daemon=True)
        listen_thread.start()

    def _listen(self):
        while True:
            message = self.queue.get(block=True)
            self._handle_message(message)

    def _handle_message(self, raw_message):
        message = build_message(raw_message)
        if self._need_to_record:
            self.record_message(message)

        self.on_receive_message(message)

    def record_message(self, message: SerialMessage):
        SQLLiteDAO.write_message(message)


