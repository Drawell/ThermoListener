import enum
from datetime import datetime


def build_message(raw_message: str):
    message = SerialMessage()

    found = False
    for message_type in MessageType:
        if len(message_type.value) < len(raw_message) and raw_message[:len(message_type.value)] == message_type.value:
            message.type = message_type
            message.text = raw_message[len(message_type.value):].strip()
            found = True
            break

    if not found:
        message.type = MessageType.SIMPLE_MESSAGE
        message.text = raw_message

    return message


class MessageType(enum.Enum):
    ERROR_MESSAGE = 'Error: '
    MODE_MESSAGE = 'Current mode: '
    MAINTAINING_TEMP_MESSAGE = 'Maintaining Temp: '
    TEMPERATURE_MESSAGE = "Temp: "
    ACTION_MESSAGE = 'Action: '
    POWER_MESSAGE = 'Power: '
    SIMPLE_MESSAGE = ''


class SerialMessage:
    def __init__(self):
        self.type = MessageType.SIMPLE_MESSAGE
        self.text = ''
        self.time = datetime.now()

    def __str__(self):
        return self.time.strftime('[%H:%M:%S.%f]') + f' {self.type.value}{self.text}'
