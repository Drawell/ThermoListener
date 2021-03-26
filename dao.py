from serial_message import SerialMessage


class SQLLiteDAO:
    def __init__(self):
        pass

    @staticmethod
    def write_message(message: SerialMessage):
        print(message.text)
