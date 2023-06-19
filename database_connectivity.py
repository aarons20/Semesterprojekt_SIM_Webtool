from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models.sim_profile import Base, SIMProfile

class DataBaseConnectivity:    
    # Initializing
    def __init__(self):
        self._engine = create_engine('sqlite:///instance/database.db')
        Session = sessionmaker(bind=self._engine)
        self._session = Session()

        Base.metadata.create_all(self._engine)
        SIMProfile.__table__.create(bind=self._engine, checkfirst=True)

        result = self._session.query(SIMProfile).first()
        if result is None:
            self._create_default_profiles()

    def _create_default_profiles(self):
        default_profiles = [
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

        for profile in default_profiles:
            self.addSIMProfile(profile)

    def addSIMProfile(self, sim_profile: SIMProfile):
        try:
            self._session.add(sim_profile)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise Exception(str(e))
                

    def getSIMProfiles(self):
        return self._session.query(SIMProfile).all()
    
    # Deleting (Calling destructor)
    def __del__(self):
        self._session.close()
        self._engine.dispose()