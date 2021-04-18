from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship

from DB.db_connection import Base
from Serial.serial_message import SerialMessage


class Session(Base):
    __tablename__ = 'session'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(60))
    mode_name = Column(String(60))
    start_date = Column(Date)
    maintaining_temperature = Column(Float, nullable=False)
    temperatures = relationship('Temperature', backref='session', lazy='subquery', cascade="all, delete-orphan")
    actions = relationship('Action', backref='session', lazy='subquery', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Session {self.id}>'


class Temperature(Base):
    __tablename__ = 'temperature'

    id = Column(Integer, autoincrement=True, primary_key=True)
    time = Column(Date)
    sensor_idx = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    session_id = Column(Integer, ForeignKey('session.id'), nullable=False)

    def __repr__(self):
        return f'<Temperature {self.id}>'

    def __str__(self):
        return self.time.strftime('[%H:%M:%S:ms]') + f' {self.type.value}{self.text}'

    @staticmethod
    def from_serial_message(message: SerialMessage):
        idx, value = message.text.split(' ')
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
    time = Column(Date)
    text = Column(String(50), nullable=False)
    session_id = Column(Integer, ForeignKey('session.id'), nullable=False)

    def __repr__(self):
        return f'<Action {self.id}>'

    @staticmethod
    def from_serial_message(message: SerialMessage):
        result = Action()
        result.time = message.time
        result.text = message.text
        return result


'''

class Template(db.Model, SerializerMixin):
    __tablename__ = 'template'

    serialize_only = ('id', 'name', 'header', 'sheets', 'end_date')
    date_format = '%Y.%m.%d'

    id = Column(Integer, Sequence('TEMPLATE_SEQ'), primary_key=True)
    name = Column(String(60))
    header = Column(String(256))
    creation_date = Column(db.Date)
    end_date = Column(db.Date)
    sheets = db.relationship('TemplateSheet', backref='template', lazy='subquery', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Template {self.id}>'


class TemplateSheet(db.Model, SerializerMixin):
    __tablename__ = 'template_sheet'

    serialize_only = ('id', 'name', 'deletable', 'header', 'price_columns', 'sps_list', 'groups', 'annotations')

    id = Column(Integer, Sequence('TEMPLATE_SHEET_SEQ'), primary_key=True)
    name = Column(String(100))
    deletable = Column(Integer, default=1)
    header = Column(String(256))

    template_id = Column(Integer, db.ForeignKey('template.id'), nullable=False)

    price_columns = relationship('PriceColumn', lazy='subquery', back_populates="sheet", cascade="all, delete-orphan")
    sps_list = relationship('SPSInSheet', lazy='subquery', back_populates="sheet", cascade="all, delete-orphan")
    groups = relationship('GroupVersionInSheet', lazy='subquery', back_populates="sheet", cascade="all, delete-orphan")
    annotations = relationship('Annotation', lazy='subquery', back_populates="sheet", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<TemplateSheet {self.id}>'


class PriceColumn(db.Model, SerializerMixin):
    __tablename__ = 'price_column'

    serialize_only = ('id', 'name', 'deletable', 'price_source', 'factor',
                      'addendum', 'sps_install', 'sps_series', 'promotion')

    id = Column(Integer, Sequence('PRICE_COLUMN_SEQ'), primary_key=True)
    sheet_id = Column(Integer, db.ForeignKey('template_sheet.id'), nullable=False)
    name = Column(String(100))
    deletable = Column(Integer, default=1)
    price_source = Column(String(15), nullable=False, default='sales_price')
    factor = Column(db.Float, nullable=False, default=1)
    addendum = Column(db.Float, nullable=False, default=0)
    instnum = Column(Integer, db.ForeignKey('KPLUS.LSPSINSTALL.instnum'), default=1)
    sernum = Column(Integer, db.ForeignKey('KPLUS.LSPSSERIES.sernum'), default=1)
    promnum = Column(Integer, db.ForeignKey('KPLUS.v_promotion.promnum'), default=1)

    sheet = relationship("TemplateSheet", lazy='subquery', back_populates="price_columns")

    sps_install = relationship("SPSInstall", lazy='subquery', back_populates="price_columns")
    sps_series = relationship("SPSSeries", lazy='subquery', back_populates="price_columns")
    promotion = relationship("Promotion", lazy='subquery', back_populates="price_columns")

    def __repr__(self):
        return f'<PriceColumn {self.id}>'


class GroupVersionInSheet(db.Model, SerializerMixin):
    __tablename__ = 'group_version_in_sheet'

    serialize_only = ('version', 'sheet_id', 'position', 'is_general_system')

    sheet_id = Column(db.Integer, db.ForeignKey('template_sheet.id'), primary_key=True)
    version = Column(db.Integer, db.ForeignKey('group_version.version'), primary_key=True)
    position = Column(db.Integer, nullable=False)
    is_general_system = Column(db.Integer, nullable=False, default=1)

    sheet = relationship("TemplateSheet", lazy='subquery', back_populates="groups")
    group_version = relationship("GroupVersion", lazy=True, back_populates="sheets")

    def __repr__(self):
        return f'<GroupVersionInSheet version:{self.version} sheet:{self.sheet_id}>'


class SPSInSheet(db.Model, SerializerMixin):
    __tablename__ = 'sps_in_sheet'

    serialize_only = ('sps', 'sheet_id', 'position', 'is_general_system')

    sheet_id = Column(db.Integer, db.ForeignKey('template_sheet.id'), primary_key=True)
    spsnum = Column(db.Integer, db.ForeignKey('KPLUS.v_sales_price.spsnum'), primary_key=True)
    position = Column(db.Integer, nullable=False)
    is_general_system = Column(db.Integer, nullable=False, default=1)

    sheet = relationship("TemplateSheet", lazy='subquery', back_populates="sps_list")
    sps = relationship("SalesPrice", lazy=True, back_populates="sheets")

    def __repr__(self):
        return f'<GroupVersionInSheet version:{self.version} sheet:{self.sheet_id}>'


class Annotation(db.Model, SerializerMixin):
    __tablename__ = 'annotation'

    serialize_only = ('id', 'sheet_id', 'text')

    id = Column(Integer, Sequence('ANNOTATION_SEQ'), primary_key=True)
    sheet_id = Column(db.Integer, db.ForeignKey('template_sheet.id'))
    text = Column(db.String(1024))
    sheet = relationship("TemplateSheet", lazy='subquery', back_populates="annotations")

    def __repr__(self):
        return f'<GroupVersionInSheet version:{self.version} sheet:{self.sheet_id}>'
'''
