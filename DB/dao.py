from datetime import datetime

from Serial.serial_message import SerialMessage
from .db_connection import get_engine
from .model import Session as ModelSession, Temperature, Action, Power
from sqlalchemy.orm import sessionmaker

#def _session_wrapper(func):


class SQLiteDAO:
    def __init__(self):
        self.engine = get_engine()
        self.SessionClass = sessionmaker(self.engine)

    def get_all_sessions(self):
        pass

    def create_session(self, session_: ModelSession):
        session_.start_date = datetime.now()
        sess_id = None
        with self.SessionClass() as sess:
            sess.add(session_)
            sess.flush()
            sess.refresh(session_)
            sess_id = session_.id
            sess.commit()

        with self.SessionClass() as sess:
            new_session = sess.query(ModelSession).get(sess_id)

        return new_session

    def add_temperature(self, temp: Temperature):
        self.add_entry(temp)

    def add_action(self, action: Action):
        self.add_entry(action)

    def add_power(self, power: Power):
        self.add_entry(power)

    def add_entry(self, entry):
        if entry is not None:
            with self.SessionClass() as session:
                session.add(entry)
                session.commit()
