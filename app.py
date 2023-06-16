from flask import Flask, render_template
from models.sim_profile import SIMProfile
from sim_reader_writer import SIMReaderWriter, SimReaderWriterStatus
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import MigrateCommand
"""



app = Flask(__name__)
sim_reader_writer = SIMReaderWriter()
"""
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return f'<User {self.username}>'
"""

@app.route('/')
@app.route('/get-updated-profiles')
def index():
    profiles = [
        SIMProfile(        
            imsi='262980000420001',
            name='hs-furtwangen.de',        
            ki='791b73b094f3ac52c80ceefdacbd9d94',
            opc='87563f95d13f412195afa674de523208'
        ),
        SIMProfile(        
            imsi='262980000420002',
            name='hs-furtwangen.de',        
            ki='baf405905b7e6ea3846a7861006bd621',
            opc='cf310e720dbf8a1f324df8c43ce4618d'
        ),
        SIMProfile(        
            imsi='262980000420003',
            name='hs-furtwangen.de',        
            ki='dd0f38f343678566a45853b43540b393',
            opc='be3c92d74ab3fd725aed576bc72895a4'
        )
    ]
    active_imsi = ""
    sim_profile = sim_reader_writer.get_sim_profile()
    if sim_profile is not None:       
        active_imsi = sim_profile.imsi
    reader_status = sim_reader_writer.reader_status()
    return render_template('index.html', 
                           profiles=profiles,
                           active_imsi = active_imsi, 
                           status = reader_status,
                           SimReaderWriterStatus=SimReaderWriterStatus)

if __name__ == '__main__':
    app.run(debug=True)
