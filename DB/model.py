from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from DB.db_connection import Base
from Serial.serial_message import SerialMessage


class Session(Base):
    __tablename__ = 'session'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(60))
    mode_name = Column(String(60))
    start_date = Column(DateTime)
    maintaining_temperature = Column(Float, nullable=False)

    temperatures = relationship('Temperature', backref='session', lazy='subquery', cascade="all, delete-orphan",
                                order_by='Temperature.time')
    powers = relationship('Power', backref='session', lazy='subquery', cascade="all, delete-orphan",
                          order_by='Power.time')
    actions = relationship('Action', backref='session', lazy='subquery', cascade="all, delete-orphan",
                           order_by='Action.time')

    def __repr__(self):
        return f'<Session {self.id}>'

    def __str__(self):
        return f'Session {self.id}: {self.mode_name}'


class Temperature(Base):
    __tablename__ = 'temperature'

    id = Column(Integer, autoincrement=True, primary_key=True)
    time = Column(DateTime)
    sensor_idx = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    session_id = Column(Integer, ForeignKey('session.id'), nullable=False)

    def __repr__(self):
        return f'<Temperature {self.id}>'

    def __str__(self):
        return self.time.strftime('[%H:%M:%S.%f]') + f'Temperature: {self.temperature}'

    @staticmethod
    def from_serial_message(message: SerialMessage):
        idx, value = message.text.split(': ')
        idx = int(idx)
        value = float(value) / 100
        result = Temperature()
        result.time = message.time
        result.sensor_idx = idx
        result.temperature = value
        return result


class Action(Base):
    __tablename__ = 'action'

    id = Column(Integer, autoincrement=True, primary_key=True)
    time = Column(DateTime)
    text = Column(String(50), nullable=False)
    session_id = Column(Integer, ForeignKey('session.id'), nullable=False)

    def __repr__(self):
        return f'<Action {self.id}>'

    def __str__(self):
        return self.time.strftime('[%H:%M:%S.%f]') + f'Action: {self.text}'

    @staticmethod
    def from_serial_message(message: SerialMessage):
        result = Action()
        result.time = message.time
        result.text = message.text
        return result


class Power(Base):
    __tablename__ = 'power'

    id = Column(Integer, autoincrement=True, primary_key=True)
    time = Column(DateTime)
    power = Column(Integer, nullable=False)
    session_id = Column(Integer, ForeignKey('session.id'), nullable=False)

    def __repr__(self):
        return f'<Power {self.id}>'

    def __str__(self):
        return self.time.strftime('[%H:%M:%S.%f]') + f'Power: {self.power}'

    @staticmethod
    def from_serial_message(message: SerialMessage):
        result = Power()
        result.time = message.time
        result.power = int(message.text)
        return result
