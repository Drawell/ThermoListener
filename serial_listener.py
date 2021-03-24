import serial
import serial.tools.list_ports


class SerialListener:
    garbage_symbols = ['\r', '\n']
    baud_rate = 9600

    def __init__(self):
        self.chosen_port = ''
        self._is_need_to_stop = False
        self._is_stopped = True

    def get_all_com_ports(self):
        ports = serial.tools.list_ports.comports()
        result = []
        for port, desc, hwid in sorted(ports):
            result.append(port)

        return result

    def choose_port(self, port_name: str):
        self.chosen_port = port_name

    def start_listening(self, callback):
        if self.chosen_port == '':
            return

        try:
            with serial.Serial(self.chosen_port, SerialListener.baud_rate, timeout=1000) as ser:
                self._is_stopped = False
                self._is_need_to_stop = False
                while not self._is_need_to_stop:
                    byte_str = ser.readline()  # read a '\n' terminated line
                    line = SerialListener._prepare_input(byte_str)
                    callback(line)
        except Exception as ex:
            raise ex
        finally:
            self._is_stopped = True
            self._is_need_to_stop = True

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
