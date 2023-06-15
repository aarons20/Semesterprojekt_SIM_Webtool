from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SIMProfile(db.Model):
    imsi = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)    
    ki = db.Column(db.String(255), nullable=False)
    opc = db.Column(db.String(255), nullable=False)

    def __init__(self, imsi, name, ki, opc):
        self.name = name        
        self.imsi = imsi        
        self.ki = ki
        self.opc = opc

    def __repr__(self):
        return f'SIMProfile(name={self.name}, imsi={self.imsi}, ki={self.ki}, opc={self.opc})'
