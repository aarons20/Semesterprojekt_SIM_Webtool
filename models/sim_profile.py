from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class SIMProfile(Base):
    __tablename__ = 'sim_profiles'

    imsi = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)    
    ki = Column(String(255), nullable=False)
    opc = Column(String(255), nullable=False)

    def __init__(self, imsi, name, ki, opc):
        self.name = name        
        self.imsi = imsi        
        self.ki = ki
        self.opc = opc

    def __repr__(self):
        return f'SIMProfile(name={self.name}, imsi={self.imsi}, ki={self.ki}, opc={self.opc})'
