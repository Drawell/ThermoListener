import random
from time import sleep

import serial
import serial.tools.list_ports
from queue import Queue
import threading


class SerialListener:
    garbage_symbols = ['\r', '\n', '\x00']
    baud_rate = 115200

    def __init__(self, serial_message_queue: Queue):
        self.chosen_port = ''
        self._is_need_to_stop = False
        self._is_stopped = True
        self.queue = serial_message_queue

    @staticmethod
    def get_all_com_ports():
        ports = serial.tools.list_ports.comports()
        result = []
        for port, desc, hwid in sorted(ports):
            result.append(port)

        return result

    def choose_port(self, port_name: str):
        self.chosen_port = port_name

    def start_listening(self):
        if self.chosen_port == '':
            return

        while self._is_need_to_stop and not self._is_stopped:
            sleep(0.1)

        self._is_need_to_stop = False
        listen_thread = threading.Thread(target=self._listen,  daemon=True)
        listen_thread.start()

    def _listen(self):
        try:
            with serial.Serial(self.chosen_port, SerialListener.baud_rate, timeout=1000) as ser:
                self._is_stopped = False
                self._is_need_to_stop = False
                while not self._is_need_to_stop:
                    byte_str = ser.readline()
                    line = SerialListener._prepare_input(byte_str)
                    self.queue.put(line)

        except Exception as ex:
            #raise ex
            self.queue.put('Error: Serial Line Error')
        finally:
            print('stopped')
            self._is_stopped = True
            self._is_need_to_stop = False

    @staticmethod
    def _prepare_input(byte_str: bytes):
        line = byte_str.decode('ansi')
        prepared = line.translate({ord(i): None for i in SerialListener.garbage_symbols})
        return prepared

    def stop_listening(self):
        self._is_need_to_stop = True
        while not self._is_stopped:
            pass

    def is_stopped(self):
        return self._is_stopped


class MockSerialListener(SerialListener):
    def __init__(self, serial_message_queue: Queue):
        super().__init__(serial_message_queue)

    def start_listening(self):
        while self._is_need_to_stop and not self._is_stopped:
            sleep(0.1)

        self._is_need_to_stop = False
        listen_thread = threading.Thread(target=self._listen,  daemon=True)
        listen_thread.start()

    def _listen(self):
        try:
            self.queue.put('Maintaining Temp: 2500')
            self.queue.put('Current mode: pid')

            while not self._is_need_to_stop:
                line = f'Power: {str(random.randint(35, 45))}\n'
                self.queue.put(line)
                sleep(0.01)
                line = f'Temp: 0: {str(random.randint(2000, 3000))}\n'
                self.queue.put(line)
                sleep(1)

        except Exception as ex:
            raise ex
        finally:
            print('stopped')
            self._is_stopped = True
            self._is_need_to_stop = True


