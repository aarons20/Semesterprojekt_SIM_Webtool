import argparse
from construct import Enum, Optional
from pySim.transport import argparse_add_reader_args, LinkBase
from pySim.cards import card_detect, SimCard, UsimCard, IsimCard
from pySim.commands import SimCardCommands

from models.sim_profile import SIMProfile
from models.sim_card import SIMCard

class SimReaderWriterStatus(Enum):
    NO_CONNECTION = 1
    READER_CONNECTED = 2
    SIM_DETECTED = 3

class SIMReaderWriter():
    def __init__(self):
        self.opts_reader = None
        self.opts_writer = None
        self.sl:LinkBase = None
        self.card = None
        self.scc=None
    
    def _refresh(self):
        option_parser = argparse.ArgumentParser(description='Legacy tool for reading some parts of a SIM card',
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        argparse_add_reader_args(option_parser)
        args = ["-p", "0"]
        self.opts_reader = option_parser.parse_args(args, None)

    def _reader_connected(self) -> bool:
        self._refresh()
        from pySim.transport.pcsc import PcscSimLink        
        try:
            self.sl = PcscSimLink(self.opts_reader.pcsc_dev)
            if self.sl is None:
                return False
            return True
        except:
            return False
        
    def _sim_detected(self) -> bool:
        if(self._reader_connected):
            try:
                self.sl.wait_for_card(1)
                self.scc = SimCardCommands(transport=self.sl)
                return True
            except:
                return False            
        else:
            return False
        
    def reader_status(self) -> SimReaderWriterStatus:
        if(self._sim_detected()):
            return SimReaderWriterStatus.SIM_DETECTED
        if(self._reader_connected()):            
            return SimReaderWriterStatus.READER_CONNECTED
        
        return SimReaderWriterStatus.NO_CONNECTION
    
    def get_sim_profile(self) -> SIMProfile:
        try:
            if(self._sim_detected()):               
                # Assuming UICC SIM
                self.scc.cla_byte = "00"
                self.scc.sel_ctrl = "0004"

                # Testing for Classic SIM or UICC
                (res, sw) = self.sl.send_apdu(self.scc.cla_byte + "a4" + self.scc.sel_ctrl + "02" + "3f00")

                if sw == '6e00':
                    # Just a Classic SIM
                    self.scc.cla_byte = "a0"
                    self.scc.sel_ctrl = "0000"
                self.card = card_detect("auto", self.scc) or SimCard(self.scc)
                (res, sw) = self.card.read_imsi()
                imsi = res
                name = ''
                ki = ''
                opc = ''
                return SIMProfile(imsi, name, ki, opc)
        except Exception as e: 
            return None        
        
    def get_sim_card_iccid(self):
        try:
            if self.card is not None:
                return self.card.read_iccid()[0]
            return None
        except: 
            return None      
    
    def write_sim(self, sim_profile: SIMProfile, sim_card: SIMCard):
        if(self._reader_connected() and self._sim_detected()):
            args = ["-p", "0", # sim reader
                    "-n", sim_profile.name, # name of network
                    "-a", sim_card.adm_key, # adm-key 
                    "-s", sim_card.iccid, # ICCID of sim
                    "-i", sim_profile.imsi, # imsi
                    "-x", "262", # mcc
                    "-y", "98", # mnc
                    "-k", sim_profile.ki, # ki
                    "-o", sim_profile.opc # opc
                    ]
            from pySim.card_handler import CardHandler, CardHandlerAuto
            from pySim_prog_fuctions import process_card, parse_options
            
            self.opts_writer = parse_options(args)
            #print(self.opts_writer)
            try:
                if self.opts_writer.card_handler_config:
                    ch = CardHandlerAuto(self.sl, self.opts_writer.card_handler_config)
                else:
                    ch = CardHandler(self.sl)
                
                card = card_detect(self.opts_writer.type, self.scc)
                if card is None:
                    raise Exception("No card found!")
                rc = process_card(self.opts_writer, True, ch, self.scc)
                
                # Something did not work as well as expected, however, lets
                # make sure the card is pulled from the reader.
                if rc != 0:
                    ch.error()
            except:
                raise
        else:
            raise Exception("No Sim connected")


def test():
    sim_reader_writer = SIMReaderWriter()
    #sim_reader_writer._reader_connected()
    #sim_profile = sim_reader_writer.get_sim_profile()
    sim_profile = SIMProfile(        
            imsi='262980000420002',
            name='hs-furtwangen.de',        
            ki='baf405905b7e6ea3846a7861006bd621',
            opc='cf310e720dbf8a1f324df8c43ce4618d'
        )
    sim_reader_writer.write_sim(sim_profile=sim_profile)
#test()