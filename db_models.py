from sqlalchemy import Column, Integer, String, Float
from db_connect import Base

class Request(Base):
    __tablename__ = 'request'

    id = Column('id',Integer, primary_key = True)
    num = Column('num',String,nullable = False)
    problem = Column('problem',String,nullable = False)
    user_id = ('user_id',Integer)

class User(Base):
    __tablename__ = 'users'

    id = Column('id',Integer, primary_key = True)
    num = Column('num',Integer,nullable = False)
    surname = Column('surname',String,nullable = False)
    password = Column('password',Integer)
    role = Column('role',Integer)
    responsibility = Column('responsibility',String)

class Machine(Base):
    __tablename__ = 'machines'

    id = Column('id',Integer,primary_key = True)
    name = Column('name',String,nullable = False)
    form = Column('form',String)
    num = Column('num',Integer)