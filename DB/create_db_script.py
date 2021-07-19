from DB.db_connection import get_engine, Base
from DB.model import *

Base.metadata.create_all(bind=get_engine())
