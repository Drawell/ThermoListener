from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
import enum
from config import db_type


def get_engine():
    db_name = 'thermo_listener'

    if db_type == 'MySQL':
        username = 'root'
        passwd = '12345'
        engine = create_engine(f'mysql+pymysql://{username}:{passwd}@localhost/{db_name}?host=localhost?port=3306')
    elif db_type == 'SQLite':
        engine = create_engine(f'sqlite:///{db_name}.db')
    else:
        engine = create_engine(f'sqlite:///{db_name}.db')

    return engine


Base = declarative_base()
