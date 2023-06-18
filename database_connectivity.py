from models.sim_profile import SIMProfile


def getSIMProfiles():
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
    return  profiles