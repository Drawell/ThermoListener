from datetime import datetime

from Serial.serial_message import SerialMessage
from .db_connection import get_engine
from .model import Session as ModelSession, Temperature, Action
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
        with self.SessionClass() as session:
            session.add(temp)
            session.commit()

    def add_action(self, action: Action):
        with self.SessionClass as session:
            session.add(action)
            session.commit()
