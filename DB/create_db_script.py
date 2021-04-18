from .db_connection import get_engine, Base
from .model import *

Base.metadata.create_all(bind=get_engine())
