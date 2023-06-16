import argparse
from construct import Enum, Optional
from pySim.transport import argparse_add_reader_args, LinkBase
from pySim.cards import card_detect, SimCard, UsimCard, IsimCard
from pySim.commands import SimCardCommands

from models.sim_profile import SIMProfile

class SimReaderWriterStatus(Enum):
    NO_CONNECTION = 1
    READER_CONNECTED = 2
    SIM_DETECTED = 3

class SIMReaderWriter():
    def __init__(self):
        self.opts = None
        self.sl:LinkBase = None
        self.card = None
    
    def _refresh(self):
        option_parser = argparse.ArgumentParser(description='Legacy tool for reading some parts of a SIM card',
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        argparse_add_reader_args(option_parser)
        args = ["-p", "0"]
        self.opts = option_parser.parse_args(args, None)

    def _reader_connected(self):
        self._refresh()
        from pySim.transport.pcsc import PcscSimLink        
        try:
            self.sl = PcscSimLink(self.opts.pcsc_dev)
            if self.sl is None:
                return False
            return True
        except:
            return False
        
    def _sim_detected(self):
        if(self._reader_connected):
            try:
                self.sl.wait_for_card(1)
                return True
            except:
                return False            
        else:
            return False
        
    def reader_status(self):
        if(self._sim_detected()):
            return SimReaderWriterStatus.SIM_DETECTED
        if(self._reader_connected()):            
            return SimReaderWriterStatus.READER_CONNECTED
        
        return SimReaderWriterStatus.NO_CONNECTION
    
    def get_sim_profile(self):
        try:
            if(self._sim_detected()):
                scc = SimCardCommands(transport=self.sl)
                # Assuming UICC SIM
                scc.cla_byte = "00"
                scc.sel_ctrl = "0004"

                # Testing for Classic SIM or UICC
                (res, sw) = self.sl.send_apdu(scc.cla_byte + "a4" + scc.sel_ctrl + "02" + "3f00")
                if sw == '6e00':
                    # Just a Classic SIM
                    scc.cla_byte = "a0"
                    scc.sel_ctrl = "0000"

                self.card = card_detect("auto", scc) or SimCard(scc)

                (res, sw) = self.card.read_imsi()
                imsi = res
                name = ''
                ki = ''
                opc = ''
                return SIMProfile(imsi, name, ki, opc)
        except:
            return None

        return None
    
    def write_sim(self, sim_profile: SIMProfile):
        print("To be implemented soon.")

def test():
    reader_connected = SIMReaderWriter().reader_connected()
    print(f"Reader connected: {reader_connected}")