#!/usr/bin/env python3
# part of the pySim-prog.py module
#

import hashlib
from optparse import OptionParser
import random
import re

from pySim.cards import _cards_classes, card_detect
from pySim.utils import swap_nibbles, rpad, derive_milenage_opc, calculate_luhn
from pySim.ts_51_011 import EF, EF_AD
from pySim.card_handler import *
from pySim.utils import *

def parse_options(args):

    parser = OptionParser(usage="usage: %prog [options]")

    parser.add_option("-d", "--device", dest="device", metavar="DEV",
                      help="Serial Device for SIM access [default: %default]",
                      default="/dev/ttyUSB0",
                      )
    parser.add_option("-b", "--baud", dest="baudrate", type="int", metavar="BAUD",
                      help="Baudrate used for SIM access [default: %default]",
                      default=9600,
                      )
    parser.add_option("-p", "--pcsc-device", dest="pcsc_dev", type='int', metavar="PCSC",
                      help="Which PC/SC reader number for SIM access",
                      default=None,
                      )
    parser.add_option("--modem-device", dest="modem_dev", metavar="DEV",
                      help="Serial port of modem for Generic SIM Access (3GPP TS 27.007)",
                      default=None,
                      )
    parser.add_option("--modem-baud", dest="modem_baud", type="int", metavar="BAUD",
                      help="Baudrate used for modem's port [default: %default]",
                      default=115200,
                      )
    parser.add_option("--osmocon", dest="osmocon_sock", metavar="PATH",
                      help="Socket path for Calypso (e.g. Motorola C1XX) based reader (via OsmocomBB)",
                      default=None,
                      )
    parser.add_option("-t", "--type", dest="type",
                      help="Card type (user -t list to view) [default: %default]",
                      default="auto",
                      )
    parser.add_option("-T", "--probe", dest="probe",
                      help="Determine card type",
                      default=False, action="store_true"
                      )
    parser.add_option("-a", "--pin-adm", dest="pin_adm",
                      help="ADM PIN used for provisioning (overwrites default)",
                      )
    parser.add_option("-A", "--pin-adm-hex", dest="pin_adm_hex",
                      help="ADM PIN used for provisioning, as hex string (16 characters long",
                      )
    parser.add_option("-e", "--erase", dest="erase", action='store_true',
                      help="Erase beforehand [default: %default]",
                      default=False,
                      )

    parser.add_option("-S", "--source", dest="source",
                      help="Data Source[default: %default]",
                      default="cmdline",
                      )

    # if mode is "cmdline"
    parser.add_option("-n", "--name", dest="name",
                      help="Operator name [default: %default]",
                      default="Magic",
                      )
    parser.add_option("-c", "--country", dest="country", type="int", metavar="CC",
                      help="Country code [default: %default]",
                      default=1,
                      )
    parser.add_option("-x", "--mcc", dest="mcc", type="string",
                      help="Mobile Country Code [default: %default]",
                      default="901",
                      )
    parser.add_option("-y", "--mnc", dest="mnc", type="string",
                      help="Mobile Network Code [default: %default]",
                      default="55",
                      )
    parser.add_option("--mnclen", dest="mnclen", type="choice",
                      help="Length of Mobile Network Code [default: %default]",
                      default="auto",
                      choices=["2", "3", "auto"],
                      )
    parser.add_option("-m", "--smsc", dest="smsc",
                      help="SMSC number (Start with + for international no.) [default: '00 + country code + 5555']",
                      )
    parser.add_option("-M", "--smsp", dest="smsp",
                      help="Raw SMSP content in hex [default: auto from SMSC]",
                      )

    parser.add_option("-s", "--iccid", dest="iccid", metavar="ID",
                      help="Integrated Circuit Card ID",
                      )
    parser.add_option("-i", "--imsi", dest="imsi",
                      help="International Mobile Subscriber Identity",
                      )
    parser.add_option("--msisdn", dest="msisdn",
                      help="Mobile Subscriber Integrated Services Digital Number",
                      )
    parser.add_option("-k", "--ki", dest="ki",
                      help="Ki (default is to randomize)",
                      )
    parser.add_option("-o", "--opc", dest="opc",
                      help="OPC (default is to randomize)",
                      )
    parser.add_option("--op", dest="op",
                      help="Set OP to derive OPC from OP and KI",
                      )
    parser.add_option("--acc", dest="acc",
                      help="Set ACC bits (Access Control Code). not all card types are supported",
                      )
    parser.add_option("--opmode", dest="opmode", type="choice",
                      help="Set UE Operation Mode in EF.AD (Administrative Data)",
                      default=None,
                      choices=['{:02X}'.format(int(m)) for m in EF_AD.OP_MODE],
                      )
    parser.add_option("-f", "--fplmn", dest="fplmn", action="append",
                      help="Set Forbidden PLMN. Add multiple time for multiple FPLMNS",
                      )
    parser.add_option("--epdgid", dest="epdgid",
                      help="Set Home Evolved Packet Data Gateway (ePDG) Identifier. (Only FQDN format supported)",
                      )
    parser.add_option("--epdgSelection", dest="epdgSelection",
                      help="Set PLMN for ePDG Selection Information. (Only Operator Identifier FQDN format supported)",
                      )
    parser.add_option("--pcscf", dest="pcscf",
                      help="Set Proxy Call Session Control Function (P-CSCF) Address. (Only FQDN format supported)",
                      )
    parser.add_option("--ims-hdomain", dest="ims_hdomain",
                      help="Set IMS Home Network Domain Name in FQDN format",
                      )
    parser.add_option("--impi", dest="impi",
                      help="Set IMS private user identity",
                      )
    parser.add_option("--impu", dest="impu",
                      help="Set IMS public user identity",
                      )
    parser.add_option("--read-imsi", dest="read_imsi", action="store_true",
                      help="Read the IMSI from the CARD", default=False
                      )
    parser.add_option("--read-iccid", dest="read_iccid", action="store_true",
                      help="Read the ICCID from the CARD", default=False
                      )
    parser.add_option("-z", "--secret", dest="secret", metavar="STR",
                      help="Secret used for ICCID/IMSI autogen",
                      )
    parser.add_option("-j", "--num", dest="num", type=int,
                      help="Card # used for ICCID/IMSI autogen",
                      )
    parser.add_option("--batch", dest="batch_mode",
                      help="Enable batch mode [default: %default]",
                      default=False, action='store_true',
                      )
    parser.add_option("--batch-state", dest="batch_state", metavar="FILE",
                      help="Optional batch state file",
                      )

    # if mode is "csv"
    parser.add_option("--read-csv", dest="read_csv", metavar="FILE",
                      help="Read parameters from CSV file rather than command line")

    parser.add_option("--write-csv", dest="write_csv", metavar="FILE",
                      help="Append generated parameters in CSV file",
                      )
    parser.add_option("--write-hlr", dest="write_hlr", metavar="FILE",
                      help="Append generated parameters to OpenBSC HLR sqlite3",
                      )
    parser.add_option("--dry-run", dest="dry_run",
                      help="Perform a 'dry run', don't actually program the card",
                      default=False, action="store_true")
    parser.add_option("--card_handler", dest="card_handler_config", metavar="FILE",
                      help="Use automatic card handling machine")

    (options, args) = parser.parse_args(args=args)

    if options.type == 'list':
        for kls in _cards_classes:
            print(kls.name)
        sys.exit(0)

    if options.probe:
        return options

    if options.source == 'csv':
        if (options.imsi is None) and (options.batch_mode is False) and (options.read_imsi is False) and (options.read_iccid is False):
            parser.error(
                "CSV mode needs either an IMSI, --read-imsi, --read-iccid or batch mode")
        if options.read_csv is None:
            parser.error("CSV mode requires a CSV input file")
    elif options.source == 'cmdline':
        if ((options.imsi is None) or (options.iccid is None)) and (options.num is None):
            parser.error(
                "If either IMSI or ICCID isn't specified, num is required")
    else:
        parser.error("Only `cmdline' and `csv' sources supported")

    if (options.read_csv is not None) and (options.source != 'csv'):
        parser.error("You cannot specify a CSV input file in source != csv")

    if (options.batch_mode) and (options.num is None):
        options.num = 0

    if (options.batch_mode):
        if (options.imsi is not None) or (options.iccid is not None):
            parser.error(
                "Can't give ICCID/IMSI for batch mode, need to use automatic parameters ! see --num and --secret for more information")

    if args:
        parser.error("Extraneous arguments")

    return options


def _digits(secret, usage, len, num):
    seed = secret + usage + '%d' % num
    s = hashlib.sha1(seed.encode())
    d = ''.join(['%02d' % x for x in s.digest()])
    return d[0:len]


def _mcc_mnc_digits(mcc, mnc):
    return '%s%s' % (mcc, mnc)


def _cc_digits(cc):
    return ('%03d' if cc > 100 else '%02d') % cc


def _isnum(s, l=-1):
    return s.isdigit() and ((l == -1) or (len(s) == l))


def _ishex(s, l=-1):
    hc = '0123456789abcdef'
    return all([x in hc for x in s.lower()]) and ((l == -1) or (len(s) == l))

def gen_parameters(opts):
    """Generates Name, ICCID, MCC, MNC, IMSI, SMSP, Ki, PIN-ADM from the
    options given by the user"""

    # MCC/MNC
    mcc = opts.mcc
    mnc = opts.mnc

    if not mcc.isdigit() or not mnc.isdigit():
        raise ValueError('mcc & mnc must only contain decimal digits')
    if len(mcc) < 1 or len(mcc) > 3:
        raise ValueError('mcc must be between 1 .. 3 digits')
    if len(mnc) < 1 or len(mnc) > 3:
        raise ValueError('mnc must be between 1 .. 3 digits')

    # MCC always has 3 digits
    mcc = lpad(mcc, 3, "0")

    # The MNC must be at least 2 digits long. This is also the most common case.
    # The user may specify an explicit length using the --mnclen option.
    if opts.mnclen != "auto":
        if len(mnc) > int(opts.mnclen):
            raise ValueError('mcc is longer than specified in option --mnclen')
        mnc = lpad(mnc, int(opts.mnclen), "0")
    else:
        mnc = lpad(mnc, 2, "0")

    # Digitize country code (2 or 3 digits)
    cc_digits = _cc_digits(opts.country)

    # Digitize MCC/MNC (5 or 6 digits)
    plmn_digits = _mcc_mnc_digits(mcc, mnc)

    if opts.name is not None:
        if len(opts.name) > 16:
            raise ValueError('Service Provider Name must max 16 characters!')

    if opts.msisdn is not None:
        msisdn = opts.msisdn
        if msisdn[0] == '+':
            msisdn = msisdn[1:]
        if not msisdn.isdigit():
            raise ValueError('MSISDN must be digits only! '
                             'Start with \'+\' for international numbers.')
        if len(msisdn) > 10 * 2:
            # TODO: Support MSISDN of length > 20 (10 Bytes)
            raise ValueError(
                'MSISDNs longer than 20 digits are not (yet) supported.')

    # ICCID (19 digits, E.118), though some phase1 vendors use 20 :(
    if opts.iccid is not None:
        iccid = opts.iccid
        if not _isnum(iccid, 19) and not _isnum(iccid, 20):
            raise ValueError('ICCID must be 19 or 20 digits !')

    else:
        if opts.num is None:
            raise ValueError('Neither ICCID nor card number specified !')

        iccid = (
            '89' +			# Common prefix (telecom)
            cc_digits +		# Country Code on 2/3 digits
            plmn_digits 		# MCC/MNC on 5/6 digits
        )

        ml = 18 - len(iccid)

        if opts.secret is None:
            # The raw number
            iccid += ('%%0%dd' % ml) % opts.num
        else:
            # Randomized digits
            iccid += _digits(opts.secret, 'ccid', ml, opts.num)

        # Add checksum digit
        iccid += ('%1d' % calculate_luhn(iccid))

    # IMSI (15 digits usually)
    if opts.imsi is not None:
        imsi = opts.imsi
        if not _isnum(imsi):
            raise ValueError('IMSI must be digits only !')

    else:
        if opts.num is None:
            raise ValueError('Neither IMSI nor card number specified !')

        ml = 15 - len(plmn_digits)

        if opts.secret is None:
            # The raw number
            msin = ('%%0%dd' % ml) % opts.num
        else:
            # Randomized digits
            msin = _digits(opts.secret, 'imsi', ml, opts.num)

        imsi = (
            plmn_digits +  # MCC/MNC on 5/6 digits
            msin			# MSIN
        )

    # SMSP
    if opts.smsp is not None:
        smsp = opts.smsp
        if not _ishex(smsp):
            raise ValueError('SMSP must be hex digits only !')
        if len(smsp) < 28*2:
            raise ValueError('SMSP must be at least 28 bytes')

    else:
        ton = "81"
        if opts.smsc is not None:
            smsc = opts.smsc
            if smsc[0] == '+':
                ton = "91"
                smsc = smsc[1:]
            if not _isnum(smsc):
                raise ValueError('SMSC must be digits only!\n \
					Start with \'+\' for international numbers')
        else:
            smsc = '00%d' % opts.country + '5555'  # Hack ...

        smsc = '%02d' % ((len(smsc) + 3)//2,) + ton + \
            swap_nibbles(rpad(smsc, 20))

        smsp = (
            'e1' +			# Parameters indicator
            'ff' * 12 +		# TP-Destination address
            smsc +			# TP-Service Centre Address
            '00' +			# TP-Protocol identifier
            '00' +			# TP-Data coding scheme
            '00'			# TP-Validity period
        )

    # ACC
    if opts.acc is not None:
        acc = opts.acc
        if not _ishex(acc):
            raise ValueError('ACC must be hex digits only !')
        if len(acc) != 2*2:
            raise ValueError('ACC must be exactly 2 bytes')

    else:
        acc = None

    # Ki (random)
    if opts.ki is not None:
        ki = opts.ki
        if not re.match('^[0-9a-fA-F]{32}$', ki):
            raise ValueError('Ki needs to be 128 bits, in hex format')
    else:
        ki = ''.join(['%02x' % random.randrange(0, 256) for i in range(16)])

    # OPC (random)
    if opts.opc is not None:
        opc = opts.opc
        if not re.match('^[0-9a-fA-F]{32}$', opc):
            raise ValueError('OPC needs to be 128 bits, in hex format')

    elif opts.op is not None:
        opc = derive_milenage_opc(ki, opts.op)
    else:
        opc = ''.join(['%02x' % random.randrange(0, 256) for i in range(16)])

    pin_adm = sanitize_pin_adm(opts.pin_adm, opts.pin_adm_hex)

    # ePDG Selection Information
    if opts.epdgSelection:
        if len(opts.epdgSelection) < 5 or len(opts.epdgSelection) > 6:
            raise ValueError('ePDG Selection Information is not valid')
        epdg_mcc = opts.epdgSelection[:3]
        epdg_mnc = opts.epdgSelection[3:]
        if not epdg_mcc.isdigit() or not epdg_mnc.isdigit():
            raise ValueError(
                'PLMN for ePDG Selection must only contain decimal digits')

    # Return that
    return {
        'name': opts.name,
        'iccid': iccid,
        'mcc': mcc,
        'mnc': mnc,
        'imsi': imsi,
        'smsp': smsp,
        'ki': ki,
        'opc': opc,
        'acc': acc,
        'pin_adm': pin_adm,
        'msisdn': opts.msisdn,
        'epdgid': opts.epdgid,
        'epdgSelection': opts.epdgSelection,
        'pcscf': opts.pcscf,
        'ims_hdomain': opts.ims_hdomain,
        'impi': opts.impi,
        'impu': opts.impu,
        'opmode': opts.opmode,
        'fplmn': opts.fplmn,
    }


def print_parameters(params):

    s = ["Generated card parameters :"]
    if 'name' in params:
        s.append(" > Name     : %(name)s")
    if 'smsp' in params:
        s.append(" > SMSP     : %(smsp)s")
    s.append(" > ICCID    : %(iccid)s")
    s.append(" > MCC/MNC  : %(mcc)s/%(mnc)s")
    s.append(" > IMSI     : %(imsi)s")
    s.append(" > Ki       : %(ki)s")
    s.append(" > OPC      : %(opc)s")
    if 'acc' in params:
        s.append(" > ACC      : %(acc)s")
    s.append(" > ADM1(hex): %(pin_adm)s")
    if 'opmode' in params:
        s.append(" > OPMODE   : %(opmode)s")
    print("\n".join(s) % params)

def process_card(opts, first, ch, scc):

    # Connect transport
    ch.get(first)

    # Get card
    card = card_detect(opts.type, scc)
    if card is None:
        print("No card detected!")
        return -1

    # Probe only
    if opts.probe:
        return 0

    # Erase if requested (not in dry run mode!)
    if opts.dry_run is False:
        if opts.erase:
            print("Formatting ...")
            card.erase()
            card.reset()

    cp = gen_parameters(opts)

    if cp is None:
        return 2
    
    print_parameters(cp)

    if opts.dry_run is False:
        # Program the card
        print("Programming ...")
        card.program(cp)
    else:
        print("Dry Run: NOT PROGRAMMING!")

    # Batch mode state update and save
    if opts.num is not None:
        opts.num += 1

    ch.done()
    return 0