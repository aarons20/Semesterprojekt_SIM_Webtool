from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class SIMCard(Base):
    __tablename__ = 'sim_cards'

    iccid = Column(String(255), primary_key=True)
    adm_key = Column(String(255), nullable=False)

    def __init__(self, iccid, adm_key):
        self.iccid = iccid        
        self.adm_key = adm_key 

    def __repr__(self):
        return f'SIMCard(iccid={self.iccid}, adm_key={self.adm_key})'
