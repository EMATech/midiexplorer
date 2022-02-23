# This Python file uses the following encoding: utf-8
#
# SPDX-FileCopyrightText: 2021-2022 Raphaël Doursenaud <rdoursenaud@free.fr>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
`MIDI Explorer`
===============

* Author(s): Raphaël Doursenaud <rdoursenaud@free.fr>
"""
import sys
import time
from typing import Any, Optional

import dearpygui.dearpygui as dpg  # https://dearpygui.readthedocs.io/en/latest/
import mido  # https://mido.readthedocs.io/en/latest/
import mido.backends.rtmidi  # For PyInstaller
from dearpygui.demo import show_demo
from dearpygui_ext.logger import mvLogger  # https://dearpygui-ext.readthedocs.io/en/latest/index.html

###
# PROGRAM CONSTANTS
###
START_TIME = time.time()  # Initialize ASAP
INIT_FILENAME = "midiexplorer.ini"
DEBUG = True

###
# MIDI STANDARD CONSTANTS
#
# Based upon the MIDI 1.0 Detailed Specification v4.2.1 (February 1996)
# #
# TODO: contribute to mido?
###

# Page 8
POWER_UP_DEFAULT = {
    "basic_channel": 1,
    "mode": 1,  # Omni On/Poly
}

# Page 10
MIDDLE_C_NOTE = 60
DEFAULT_VELOCITY = 64
NOTE_OFF_VELOCITY = 0

# Page T-3
CONTROLLER_NUMBERS = {
    0: "Bank Select",
    1: "Modulation wheel or lever",
    2: "Breath controller",
    3: "Undefined",
    4: "Foot controller",
    5: "Portamento time",
    6: "Data entry MSB",
    7: "Channel Volume",  # formerly Main Volume
    8: "Balance",
    9: "Undefined",
    10: "Pan",
    11: "Expression Controller",
    12: "Effect Control 1",
    13: "Effect Control 2",
    14: "Undefined",
    15: "Undefined",
    16: "General Purpose Controller 1",
    17: "General Purpose Controller 2",
    18: "General Purpose Controller 3",
    19: "General Purpose Controller 4",
    20: "Undefined",
    21: "Undefined",
    22: "Undefined",
    23: "Undefined",
    24: "Undefined",
    25: "Undefined",
    26: "Undefined",
    27: "Undefined",
    28: "Undefined",
    29: "Undefined",
    30: "Undefined",
    31: "Undefined",
    # LSB for values 0-31
    32: "Bank Select LSB",
    33: "Modulation wheel or lever LSB",
    34: "Breath controller LSB",
    35: "Undefined LSB (3)",
    36: "Foot controller LSB",
    37: "Portamento time LSB",
    38: "Data entry LSB",
    39: "Channel Volume LSB",  # formerly Main Volume
    40: "Balance LSB",
    41: "Undefined LSB (9)",
    42: "Pan LSB",
    43: "Expression Controller LSB",
    44: "Effect Control 1 LSB",
    45: "Effect Control 2 LSB",
    46: "Undefined LSB (14)",
    47: "Undefined LSB (15)",
    48: "General Purpose Controller 1 LSB",
    49: "General Purpose Controller 2 LSB",
    50: "General Purpose Controller 3 LSB",
    51: "General Purpose Controller 4 LSB",
    52: "Undefined LSB (20)",
    53: "Undefined LSB (21)",
    54: "Undefined LSB (22)",
    55: "Undefined LSB (23)",
    56: "Undefined LSB (24)",
    57: "Undefined LSB (25)",
    58: "Undefined LSB (26)",
    59: "Undefined LSB (27)",
    60: "Undefined LSB (28)",
    61: "Undefined LSB (29)",
    62: "Undefined LSB (30)",
    63: "Undefined LSB (31)",
    64: "Damper pedal (sustain)",
    65: "Portamento On/Off",
    66: "Sostenuto",
    67: "Soft pedal",
    68: "Legato Footswitch",  # vv = 00-3F:Normal, 40-7F: Legatto
    69: "Hold 2",
    70: "Sound Controller 1",  # default: Sound Variation
    71: "Sound Controller 2",  # default: Timbre/Harmonic Intensity
    72: "Sound Controller 3",  # default: Release Time
    73: "Sound Controller 4",  # default: Attack Time
    74: "Sound Controller 5",  # default: Brightness
    75: "Sound Controller 6",  # no defaults
    76: "Sound Controller 7",  # no defaults
    77: "Sound Controller 8",  # no defaults
    78: "Sound Controller 9",  # no defaults
    79: "Sound Controller 10",  # no defaults
    80: "General Purpose Controller 5",
    81: "General Purpose Controller 6",
    82: "General Purpose Controller 7",
    83: "General Purpose Controller 8",
    84: "Portamento Control",
    85: "Undefined",
    86: "Undefined",
    87: "Undefined",
    88: "Undefined",
    89: "Undefined",
    90: "Undefined",
    91: "Effects 1 Depth",  # formerly External Effects Depth
    92: "Effects 2 Depth",  # formerly Tremolo Depth
    93: "Effects 3 Depth",  # formerly Chorus Depth
    94: "Effects 4 Depth",  # formerly Celeste (Detune) Depth
    95: "Effects 5 Depth",  # formerly Phaser Depth
    96: "Data increment",
    97: "Data decrement",
    98: "Non-Registered Parameter Number LSB",
    99: "Non-Registered Parameter Number MSB",
    100: "Resistered Parameter Number LSB",
    101: "Resistered Parameter Number MSB",
    102: "Undefined",
    103: "Undefined",
    104: "Undefined",
    105: "Undefined",
    106: "Undefined",
    107: "Undefined",
    108: "Undefined",
    109: "Undefined",
    110: "Undefined",
    111: "Undefined",
    112: "Undefined",
    113: "Undefined",
    114: "Undefined",
    115: "Undefined",
    116: "Undefined",
    117: "Undefined",
    118: "Undefined",
    119: "Undefined",
    # Reserved for Channel Mode Messages
    120: "Reserved for Channel Mode Messages",
    121: "Reserved for Channel Mode Messages",
    122: "Reserved for Channel Mode Messages",
    123: "Reserved for Channel Mode Messages",
    124: "Reserved for Channel Mode Messages",
    125: "Reserved for Channel Mode Messages",
    126: "Reserved for Channel Mode Messages",
    127: "Reserved for Channel Mode Messages",
}

# Page T-4
REGISTERED_PARAMETER_NUMBERS = {
    # LSB only since MSB is always 0x00
    0x00: "Pitch Bend Sensitivity",
    0x01: "Fine Tuning",
    0x02: "Coarse Tuning",
    0x03: "Tuning Program Select",
    0x04: "Tuning Bank Select",
}

# Page T-5
# Only valid for the device’s Basic Channel Number
CHANNEL_MODE_MESSAGES = {
    120: "All Sound Off",  # 0
    121: "Reset All Controllers",  # 0
    122: "Local Control",  # 0, Local Control Off. 127, Local Control On.
    123: "All Notes Off",  # 0
    124: "Omni Mode Off (All Notes Off)",  # 0
    125: "Omni Mode On (All Notes Off)",  # 0
    126: "Mono Mode On (Poly Mode Off) (All Notes Off)",
    # M, where M is the number of channels. 0, the number of channels equals the number of voices in the receiver.
    127: "Poly Mode On (Mono Mode Off) (All Notes Off)",
}

# Page T-6
SYSTEM_COMMON_MESSAGES = {
    0xF1: "MIDI Time Code Quarter Frame",
    0xF2: "Song Position Pointer",
    0xF3: "Song Select",
    0xF4: "Undefined",
    0xF5: "Undefined",
    0xF6: "Tune Request",
    0xF7: "EOX: \"End of System Exclusive\" flag",
}

# Page T-7
SYSTEM_REAL_TIME_MESSAGES = {
    0xF8: "Timing Clock",
    0xF9: "Undefined",
    0xFA: "Start",
    0xFB: "Continue",
    0xFC: "Stop",
    0xFD: "Undefined",
    0xFE: "Active Sensing",
    0xFF: "System Reset",
}

# Page T-9
DEFINED_UNIVERSAL_SYSTEM_EXCLUSIVE_MESSAGES_NON_REAL_TIME_SUB_ID_1 = {  # 0x7E
    0x00: "Unused",
    0x01: "Sample Dump Header",
    0x02: "Sample Data Packet",
    0x03: "Sample Dump Request",
    0x04: "MIDI Time Code",  # SUB-ID #2
    0x05: "Sample Dump Extensions",  # SUB-ID #2
    0x06: "General Information",  # SUB-ID #2
    0x07: "File Dump",  # SUB-ID #2
    0x08: "MIDI Tuning Standard",  # SUB-ID #2
    0x09: "General MIDI",  # SUB-ID #2
    0x7B: "End of File",
    0x7C: "Wait",
    0x7D: "Cancel",
    0x7E: "NAK",
    0x7F: "ACK",
}
MIDI_TIME_CODE_SUB_ID_2 = {  # 0x04
    0x00: "Special",
    0x01: "Punch In Points",
    0x02: "Punch Out Points",
    0x03: "Delete Punch In Points",
    0x04: "Delete Punch Out Points",
    0x05: "Event Start Point",
    0x06: "Event Stop Point",
    0x07: "Event Start Points with additional info.",
    0x08: "Event Stop Points with additional info.",
    0x09: "Delete Event Start Point",
    0x0A: "Delete Event Stop Point",
    0x0B: "Cue Points",
    0x0C: "Cue Points with additional info.",
    0x0D: "Delete Cue Point",
    0x0E: "Event Name in additional info.",
}
SAMPLE_DUMP_EXTENSIONS_SUB_ID_2 = {  # 0x05
    0x01: "Multiple Loop Points",
    0x02: "Loop Points Request",
}
GENERAL_INFORMATION_SUB_ID_2 = {  # 0x06
    0x01: "Identity Request",
    0x02: "Identity Reply",
}
FILE_DUMP_SUB_ID_2 = {  # 0x07
    0x01: "Header",
    0x02: "Data Packet",
    0x03: "Request",
}
MIDI_TUNING_STANDARD_SUB_ID_2 = {  # 0x08
    0x00: "Bulk Dump Request",
    0x01: "Bulk Dump Reply",
}
GENERAL_MIDI_SUB_ID_2 = {  # 0x09
    0x01: "General MIDI System On",
    0x02: "General MIDI System Off",
}

# Page T-10
DEFINED_UNIVERSAL_SYSTEM_EXCLUSIVE_MESSAGES_REAL_TIME_SUB_ID_1 = {  # 0x7F
    0x00: "Unused",
    0x01: "MIDI Time Code",  # SUB-ID #2
    0x02: "MIDI Show Control",  # SUB-ID #2
    0x03: "Notation Information",  # SUB-ID #2
    0x04: "Device Control",  # SUB-ID #2
    0x05: "Real Time MTC Cueing",  # SUB-ID #2
    0x06: "MIDI Machine Control Commands",  # SUB-ID #2
    0x07: "MIDI Machine Control Responses",  # SUB-ID #2
    0x08: "MIDI Tuning Standard",  # SUB-ID #2
}

REAL_TIME_MIDI_TIME_CODE_SUB_ID_2 = {  # 0x01
    0x01: "Full Message",
    0x02: "User Bits",
}

REAL_TIME_SHOW_CONTROL_SUB_ID_2 = {  # 0x02
    0x00: "MSC Extensions",
    0X01: "MSC Commands",  # FIXME: extract from MSC spec
}

REAL_TIME_NOTATION_INFORMATION_SUB_ID_2 = {  # 0x03
    0x01: "Bar Number",
    0x02: "Time Signature (Immediate)",
    0x03: "Time Signature (Delayed)",
}

REAL_TIME_DEVICE_CONTROL = {  # 0x04
    0x01: "Master Volume",
    0x02: "Master Balance",
}

REAL_TIME_MTC_CUEING = {  # 0x05
    0x00: "Special",
    0x01: "Punch In Points",
    0x02: "Punch Out Points",
    0x03: "(Reserved)",
    0x04: "(Reserved)",
    0x05: "Event Start Point",
    0x06: "Event Stop Point",
    0x07: "Event Start Points with additional info.",
    0x08: "Event Stop Points with additional info.",
    0x09: "(Reserved)",
    0x0A: "(Reserved)",
    0x0B: "Cue Points",
    0x0C: "Cue Points with additional info.",
    0x0D: "(Reserved)",
    0x0E: "Event Name in additional info.",
}

REAL_TIME_MIDI_MACHINE_CONTROL_COMMANDS = {  # 0x06
    0x00: "MMC Commands",  # FIXME: extract from MMC spec
}

REAL_TIME_MIDI_MACHINE_CONTROL_RESPONSES = {  # 0x07
    0x00: "MMC Responses",  # FIXME: extract from MMC spec
}

REAL_TIME_MIDI_TUNING_STANDARD = {  # 0x08
    0x02: "Note Change",
}

# Page T-11
SYSTEM_EXCLUSIVE_MANUFACTURER_ID = {
    # 3-byte IDs
    0x00: {
        0x00: {  # American Group
            0x01: "Time Warner Interactive",

            0x07: "Digital Music Corp.",
            0x08: "IOTA Systems",
            0x09: "New England Digital",
            0x0A: "Artisyn",
            0x0B: "IVL Technologies",
            0x0C: "Southern Music Systems",
            0x0D: "Lake Butler Sound Company",
            0x0E: "Alesis",

            0x10: "DOD Electronics",
            0x11: "Studer-Editech",

            0x14: "Perfect Fretworks",
            0x15: "KAT",
            0x16: "Opcode",
            0x17: "Rane Corp.",
            0x18: "Anadi Inc.",
            0x19: "KMX",
            0x1A: "Allen & Heath Brenell",
            0x1B: "Peavey Electronics",
            0x1C: "360 Systems",
            0x1D: "Spectrum Design and Development",
            0x1E: "Marquis Music",
            0x1F: "Zeta Systems",
            0x20: "Axxes",
            0x21: "Orban",

            0x24: "KTI",
            0x25: "Breakaway Technologies",
            0x26: "CAE",

            0x29: "Rocktron Corp.",
            0x2A: "PianoDisc",
            0x2B: "Cannon Research Group",

            0x2D: "Regors Instrument Corp.",
            0x2E: "Blue Sky Logic",
            0x2F: "Encore Electronics",
            0x30: "Uptown",
            0x31: "Voce",
            0x32: "CTI Audio, Inc. (Music. Intel Dev.)",
            0x33: "S&S Research",
            0x34: "Broderbund Software, Inc.",
            0x35: "Allen Organ Co.",

            0x37: "Music Quest",
            0x38: "APHEX",
            0x39: "Gallien Krueger",
            0x3A: "IBM",

            0x3C: "Hotz Instruments Technologies",
            0x3D: "ETA Lighting",
            0x3E: "NSI Corporation",
            0x3F: "Ad Lib, Inc.",
            0x40: "Richmond Sound Design",
            0x41: "Microsoft",
            0x42: "The Software Toolworks",
            0x43: "Niche/RJMG",
            0x44: "Intone",

            0x47: "GT Electronics/Groove Tubes",
            # TODO: Report to MMA that 0x4F is duplicated here as "InterMIDI, Inc." instead of just "InterMIDI"?
            0x49: "Timeline Vista",
            0x4A: "Mesa Boogie",

            0x4C: "Sequoia Development",
            0x4D: "Studio Electrionics",
            0x4E: "Euphonix",
            0x4F: "InterMIDI",
            0x50: "MIDI Solutions",
            0x51: "3DO Company",
            0x52: "Lightwave Research",
            0x53: "Micro-W",
            0x54: "Spectral Synthesis",
            0x55: "Lone Wolf",
            0x56: "Studio Technologies",
            0x57: "Peterson EMP",
            0x58: "Atari",
            0x59: "Marion Systems",
            0x5A: "Design Event",
            0x5B: "Winjammer Software",
            0x5C: "AT&T Bell Labs",
            0x5E: "Symetrix",
            0x5F: "MIDI the world",
            0x60: "Desper Products",
            0x61: "Micros ’N MIDI",
            0x62: "Accordians Intl",
            0x63: "EuPhonics",
            0x64: "Musonix",
            0x65: "Turtle Beach Systems",
            0x66: "Mackie Designs",
            0x67: "Compuserve",
            0x68: "BES Technologies",
            0x69: "QRS Music Rolls",
            0x6A: "P G Music",
            0x6B: "Sierra Semiconductor",
            0x6C: "EpiGraf Audio Visual",
            0x6D: "Electronics Deiversified",
            0x6E: "Tune 1000",
            0x6F: "Advanced Micro Devices",
            0x70: "Mediamation",
            0x71: "Sabine Music",
            0x72: "Woog Labs",
            0x73: "Micropolis",
            0x74: "Ta Horng Musical Inst.",
            0x75: "eTek (formerly Forte)",
            0x76: "Electrovoice",
            0x77: "Midisoft",
            0x78: "Q-Sound Labs",
            0x79: "Westrex",
            0x7A: "NVidia",
            0x7B: "ESS Technology",
            0x7C: "MediaTrix Peripherals",
            0x7D: "Brooktree",
            0x7E: "Otari",
            0x7F: "Key Electronics",
            0x80: "Crystalake Multimedia",
            0x81: "Crystal Semiconductor",
            0x82: "Rockwell Semiconductor",
        },
        0x20: {  # European Group
            0x00: "Dream",
            0x01: "Strand Lighting",
            0x02: "Amek Systems",

            0x04: "Böhm Electronic",

            0x06: "Trident Audio",
            0x07: "Real World Studio",

            0x09: "Yes Technology",
            0x0A: "Automatica",
            0x0B: "Bontempi/Farfisa",
            0x0C: "F.B.T. Elettronica",
            0x0D: "MidiTemp",
            0x0E: "LA Audio (Larking Audio)",
            0x0F: "Zero 88 Lighting Limited",
            0x10: "Micon Audio Electronics GmbH",
            0x11: "Forefront Technology",

            0x13: "Kenton Electronics",

            0x15: "ADB",
            0x16: "Marshall Products",
            0x17: "DDA",
            0x18: "BSS",
            0x19: "MA Lighting Technology",
            0x1A: "Fatar",
            0x1B: "QSC Audio",
            0x1C: "Artisan Classic Organ",
            0x1D: "Orla Spa",
            0x1E: "Pinnacle Audio",
            0x1F: "TC Electronics",
            0x20: "Doepfer Musikelektronik",
            0x21: "Creative Technology Pte",
            0x22: "Minami/Seiyddo",
            0x23: "Goldstar",
            0x24: "Midisoft s.a.s. di M. Cima",
            0x25: "Samick",
            0x26: "Penny and Giles",
            0x27: "Acorn Computer",
            0x28: "LSC Electronics",
            0x29: "Novation EMS",
            0x2A: "Samkyung Mechatroncis",
            0x2B: "Medeli Electronics",
            0x2C: "Charlie Lab",
            0x2D: "Blue Chip Music Tech",
            0x2E: "BBE OH Corp",
        }
    },

    # 1-byte IDs

    # American Group
    0x01: "Sequencial",
    0x02: "IDP",
    0x03: "Voyetra/Octave-Plateau",
    0x04: "Moog",
    0x05: "Passport Designs",
    0x06: "Lexicon",
    0x07: "Kurzweil",
    0x08: "Fender",
    0x09: "Gulbransen",
    0x0A: "AKG Acoustics",
    0x0B: "Voyce Music",
    0x0C: "Waveframe Corp",
    0x0D: "ADA Signal Processors",
    0x0E: "Garfield Electronics",
    0x0F: "Ensoniq",
    0x10: "Oberheim",
    0x11: "Apple Computer",
    0x12: "Grey Matter Response",
    0x13: "Digidesign",
    0x14: "Palm Tree Instruments",
    0x15: "JLCooper Electronics",
    0x16: "Lowrey",
    0x17: "Adams-Smith",
    0x18: "Emu Systems",
    0x19: "Harmony Systems",
    0x1A: "ART",
    0x1B: "Baldwin",
    0x1C: "Eventide",
    0x1D: "Inventronics",

    0x1F: "Clarity",

    # European Group
    0x20: "Passac",
    0x21: "SIEL",
    0x22: "Synthaxe",

    0x24: "Hohner",
    0x25: "Twister",
    0x26: "Solton",
    0x27: "Jellinghaus MS",
    0x28: "Southworth Music Systems",
    0x29: "PPG",
    0x2A: "JEN",
    0x2B: "SSL Limited",
    0x2C: "Audio Veritrieb",

    0x2F: "Elka",
    0x30: "Dynacord",
    0x31: "Viscount",

    0x33: "Clavia Digital Instruments",
    0x34: "Audio Architecture",
    0x35: "General Music Corp.",

    0x39: "Soundcraft Electronics",

    0x3B: "Wersi",
    0x3C: "Avab Electronik Ab",
    0x3D: "Digigram",
    0x3E: "Waldorf Electronics",
    0x3F: "Quasimidi",

    # Japanese Group
    0x40: "Kawai",
    0x41: "Roland",
    0x42: "Korg",
    0x43: "Yamaha",
    0x44: "Casio",

    0x46: "Kamiya Studio",
    # Shigenori Kamiya. Worked with Roland and made MIDI sequence software and tone editors such as Odyssey-K for the MSX Computer
    0x47: "Akai",
    0x48: "Japan Victor",  # JVC
    0x49: "Mesosha",
    0x4A: "Hoshino Gakki",  # Ibanez & Tama
    0x4B: "Fujitsu Elect",
    0x4C: "Sony",
    0x4D: "Nisshin Onpa",  # Maxon
    0x4E: "TEAC",  # Tascam

    0x50: "Matsushita Electric",  # Panasonic
    0x51: "Fostex",
    0x52: "Zoom",
    0x53: "Midori Electronics",
    0x54: "Matsushita Communication Industrial",  # Panasonic
    0x55: "Suzuki Musical Inst. Mfg."

}

###
# GLOBAL VARIABLES
#
# FIXME: global variables should ideally be eliminated as they are a poor programming style0
###
global logger, log_win, previous_timestamp, probe_data_counter
previous_timestamp = START_TIME
probe_data_counter = 0


###
# DEAR PYGUI CALLBACKS
###
def callback(sender: int | str, app_data: Any, user_data: Optional[Any]) -> None:
    """
    Generic Dear PyGui callback for debug purposes
    :param sender: argument is used by DPG to inform the callback
                   which item triggered the callback by sending the tag
                   or 0 if trigger by the application.
    :param app_data: argument is used DPG to send information to the callback
                     i.e. the current value of most basic widgets.
    :param user_data: argument is Optionally used to pass your own python data into the function.
    :return:
    """
    # Debug
    logger.log_debug(f"Entering {sys._getframe().f_code.co_name}:")
    logger.log_debug(f"\tSender: {sender!r}")
    logger.log_debug(f"\tApp data: {app_data!r}")
    logger.log_debug(f"\tUser data: {user_data!r}")


def link_callback(sender: int | str,
                  app_data: (dpg.mvNodeAttribute, dpg.mvNodeAttribute),
                  user_data: Optional[Any]) -> None:
    # Debug
    logger.log_debug(f"Entering {sys._getframe().f_code.co_name}:")
    logger.log_debug(f"\tSender: {sender!r}")
    logger.log_debug(f"\tApp data: {app_data!r}")
    logger.log_debug(f"\tUser data: {user_data!r}")

    pin1: dpg.mvNodeAttribute = app_data[0]
    pin2: dpg.mvNodeAttribute = app_data[1]
    node1_label, pin1_label, node2_label, pin2_label = _nodes_labels(pin1, pin2)

    logger.log_debug(f"Connection between pins: '{pin1}' & '{pin2}'.")

    # Only allow one link per pin for now
    for children in dpg.get_item_children(dpg.get_item_parent(dpg.get_item_parent(pin1)), 0):
        if dpg.get_item_info(children)['type'] == 'mvAppItemType::mvNodeLink':
            link_conf = dpg.get_item_configuration(children)
            if pin1 == link_conf['attr_1'] or pin2 == link_conf['attr_1'] or \
                    pin1 == link_conf['attr_2'] or pin2 == link_conf['attr_2']:
                logger.log_warning("Only one connection per pin is allowed at the moment.")
                return

    # Connection
    port = None
    direction = None
    probe_pin = None
    if "IN_" in pin1_label:
        direction = pin1_label[:2]  # Extract 'IN'
        port_name = pin1_label[3:]  # Filter out 'IN_'
        logger.log_info(f"Opening MIDI input: {port_name}.")
        port = mido.open_input(port_name)
        probe_pin = pin2
    elif "OUT_" in pin2_label:
        direction = pin2_label[:3]  # Extract 'OUT'
        port_name = pin2_label[4:]  # Filter out 'OUT_'
        logger.log_info(f"Opening MIDI output: {port_name}.")
        port = mido.open_output(port_name)
        probe_pin = pin1
    else:
        logger.log_warning(f"{pin1_label} or {pin2_label} is not a hardware port!")
    if port:
        logger.log_debug(f"Successfully opened {port!r}. Attaching it to the probe.")
        pin_user_data = {direction: port}
        dpg.set_item_user_data(probe_pin, pin_user_data)
        logger.log_debug(f"Attached {dpg.get_item_user_data(probe_pin)} to the {probe_pin} pin user data.")

        dpg.add_node_link(pin1, pin2, parent=sender)
        dpg.configure_item(pin1, shape=dpg.mvNode_PinShape_TriangleFilled)
        dpg.configure_item(pin2, shape=dpg.mvNode_PinShape_TriangleFilled)

        logger.log_info(f"Connected \"{node1_label}: {_get_pin_text(pin1)}\" to "
                        f"\"{node2_label}: {_get_pin_text(pin2)}\".")


# callback runs when user attempts to disconnect attributes
def delink_callback(sender: int | str, app_data: dpg.mvNodeLink, user_data: Optional[Any]) -> None:
    # Debug
    logger.log_debug(f"Entering {sys._getframe().f_code.co_name}:")
    logger.log_debug(f"\tSender: {sender!r}")
    logger.log_debug(f"\tApp data: {app_data!r}")
    logger.log_debug(f"\tUser data: {user_data!r}")

    # Get the pins that this link was connected to
    conf = dpg.get_item_configuration(app_data)
    pin1: dpg.mvNodeAttribute = conf['attr_1']
    pin2: dpg.mvNodeAttribute = conf['attr_2']
    node1_label, pin1_label, node2_label, pin2_label = _nodes_labels(pin1, pin2)

    logger.log_debug(f"Disconnection between pins: '{pin1}' & '{pin2}'.")

    # Disconnection
    direction = None
    probe_pin = None
    if "IN_" in pin1_label:
        direction = pin1_label[:2]  # Extract 'IN'
        probe_pin = pin2
    elif "OUT_" in pin2_label:
        direction = pin2_label[:3]  # Extract 'OUT'
        probe_pin = pin1
    else:
        logger.log_warning(f"{pin1_label} or {pin2_label} is not a hardware port!")
    if direction:
        pin_user_data = dpg.get_item_user_data(probe_pin)
        port = pin_user_data[direction]

        logger.log_info(f"Closing & Detaching MIDI port {port} from the probe {direction} pin.")

        del pin_user_data[direction]
        dpg.set_item_user_data(probe_pin, pin_user_data)
        port.close()

        logger.log_debug(f"Deleting link {app_data!r}.")

        dpg.delete_item(app_data)

        dpg.configure_item(pin1, shape=dpg.mvNode_PinShape_Triangle)
        dpg.configure_item(pin2, shape=dpg.mvNode_PinShape_Triangle)

        logger.log_info(f"Disconnected \"{node1_label}: {_get_pin_text(pin1)}\" from "
                        f"\"{node2_label}: {_get_pin_text(pin2)}\".")


def _toggle_log() -> None:
    dpg.configure_item(log_win, show=not dpg.is_item_visible(log_win))


def _decode(sender: int | str, app_data: Any) -> None:
    try:
        decoded = repr(mido.Message.from_hex(app_data))
    except (TypeError, ValueError) as e:
        decoded = f"Warning: {e!s}"
        pass

    logger.log_debug(f"Raw message {app_data} decoded to: {decoded}.")

    dpg.set_value('generator_decoded_message', decoded)


###
# PROGRAM FUNCTIONS
###
def _init_logger() -> None:
    # TODO: allow logging to file
    # TODO: append/overwrite

    global logger, log_win

    with dpg.window(
            tag='log_win',
            label="Log",
            width=1920,
            height=225,
            pos=[0, 815],
            show=DEBUG,
    ) as log_win:
        logger = mvLogger(log_win)
    if DEBUG:
        logger.log_level = 0  # TRACE
    else:
        logger.log_level = 2  # INFO

    logger.log_debug(f"Application started at {START_TIME}")


def _init_midi() -> None:
    mido.set_backend('mido.backends.rtmidi')

    logger.log_debug(f"Using {mido.backend.name}")
    logger.log_debug(f"RtMidi APIs: {mido.backend.module.get_api_names()}")


def _sort_ports(names: list) -> list | None:
    # TODO: extract the ID
    # TODO: add option to sort by ID rather than name
    # FIXME: do the sorting in the GUI to prevent disconnection of existing I/O?
    return sorted(set(names))


def _nodes_labels(pin1, pin2) -> tuple[str | None, str | None, str | None, str | None]:
    pin1_label = dpg.get_item_label(pin1)
    node1_label = dpg.get_item_label(dpg.get_item_parent(pin1))
    pin2_label = dpg.get_item_label(pin2)
    node2_label = dpg.get_item_label(dpg.get_item_parent(pin2))

    logger.log_debug(f"Identified pin1 '{pin1}' as '{pin1_label}' from '{node1_label}' node and "
                     f"pin2 '{pin2}' as '{pin2_label}' from '{node2_label}'.")

    return node1_label, pin1_label, node2_label, pin2_label


def _refresh_midi_ports() -> None:
    dpg.configure_item(refresh_midi_modal, show=False)  # Close popup

    midi_inputs = _sort_ports(mido.get_input_names())

    logger.log_debug(f"Available MIDI inputs: {midi_inputs}")

    midi_outputs = _sort_ports(mido.get_output_names())

    logger.log_debug(f"Available MIDI outputs: {midi_outputs}")

    # FIXME: do the sorting in the GUI to prevent disconnection of existing I/O?
    # Delete links
    dpg.delete_item(connections_editor, children_only=True, slot=0)

    # Delete ports
    dpg.delete_item(inputs_node, children_only=True)
    dpg.delete_item(outputs_node, children_only=True)

    for midi_in in midi_inputs:
        with dpg.node_attribute(label="IN_" + midi_in,
                                attribute_type=dpg.mvNode_Attr_Output,
                                shape=dpg.mvNode_PinShape_Triangle,
                                parent=inputs_node):
            dpg.add_text(midi_in)
            with dpg.popup(dpg.last_item()):
                dpg.add_button(label=f"Remove {midi_in} input")  # TODO

    for midi_out in midi_outputs:
        with dpg.node_attribute(label="OUT_" + midi_out,
                                attribute_type=dpg.mvNode_Attr_Input,
                                shape=dpg.mvNode_PinShape_Triangle,
                                parent=outputs_node):
            dpg.add_text(midi_out)
            with dpg.popup(dpg.last_item()):
                dpg.add_button(label=f"Remove {midi_out} output")  # TODO


def _save_init() -> None:
    dpg.save_init_file(INIT_FILENAME)


def _get_pin_text(pin: int | str) -> None:
    return dpg.get_value(dpg.get_item_children(pin, 1)[0])


def _add_probe_data(timestamp: float, source: str, data: mido.Message) -> None:
    # TODO: insert new data at the top of the table
    # TODO: color coding by event type
    global previous_timestamp, probe_data_counter

    previous_data = probe_data_counter
    probe_data_counter += 1

    with dpg.table_row(parent='probe_data_table', label=f'probe_data_{probe_data_counter}',
                       before=f'probe_data_{previous_data}'):
        # Timestamp (ms)
        dpg.add_text((timestamp - START_TIME) * 1000)
        # Delta (ms)
        # In polling mode we are bound to the frame rendering time.
        # For reference: 60 FPS ~= 16.7 ms, 120 FPS ~= 8.3 ms
        if previous_timestamp is not None:
            dpg.add_text((timestamp - previous_timestamp) * 1000)
        else:
            dpg.add_text("0.0")
        previous_timestamp = timestamp
        # Source
        dpg.add_selectable(label="source", span_columns=True)
        # Raw message
        dpg.add_text(data.hex())
        # Decoded message
        if DEBUG:
            dpg.add_text(repr(midi_data))
        # Channel
        if hasattr(data, 'channel'):
            dpg.add_text(data.channel)
            _mon_blink(data.channel)
        else:
            dpg.add_text("Global")
            _mon_blink('s')
        # Status
        dpg.add_text(data.type)
        _mon_blink(data.type)
        # Data 1 & 2
        if 'note' in data.type:
            dpg.add_text(data.note)  # TODO: decode to human readable
            dpg.add_text(data.velocity)
            if dpg.get_value('zero_velocity_note_on_is_note_off') and data.velocity == NOTE_OFF_VELOCITY:
                _mon_blink('note_off')
        elif 'control' in data.type:
            dpg.add_text(data.control)  # TODO: decode to human readable
            dpg.add_text(data.value)
        elif 'pitchwheel' in data.type:
            dpg.add_text(data.pitch)
            dpg.add_text("")
        elif 'sysex' in data.type:
            dpg.add_text(data.data)
            dpg.add_text("")  # TODO: decode device ID
        else:
            # TODO: decode other types
            dpg.add_text("")
            dpg.add_text("")

    # TODO: per message type color
    # dpg.highlight_table_row(table_id, i, [255, 0, 0, 100])

    # Autoscroll
    if dpg.get_value('probe_data_table_autoscroll'):
        dpg.set_y_scroll('act_det', -1.0)


def _mon_blink(channel: int | str) -> None:
    global START_TIME
    now = time.time() - START_TIME
    delay = dpg.get_value('blink_duration')
    target = f"mon_{channel}_active_until"
    until = now + delay
    dpg.set_value(target, until)
    dpg.bind_item_theme(f"mon_{channel}", '__red')
    # logger.log_debug(f"Current time:{time.time() - START_TIME}")
    # logger.log_debug(f"Blink {delay} until: {dpg.get_value(target)}")


def _update_blink_status():
    for channel in range(16):
        now = time.time() - START_TIME
        if dpg.get_value(f"mon_{channel}_active_until") < now:
            dpg.bind_item_theme(f"mon_{channel}", None)
    if dpg.get_value('mon_s_active_until') < now:
        dpg.bind_item_theme('mon_s', None)
    if dpg.get_value('mon_active_sensing_active_until') < now:
        dpg.bind_item_theme('mon_active_sensing', None)
    if dpg.get_value('mon_note_off_active_until') < now:
        dpg.bind_item_theme('mon_note_off', None)
    if dpg.get_value('mon_note_on_active_until') < now:
        dpg.bind_item_theme('mon_note_on', None)
    if dpg.get_value('mon_polytouch_active_until') < now:
        dpg.bind_item_theme('mon_polytouch', None)
    if dpg.get_value('mon_control_change_active_until') < now:
        dpg.bind_item_theme('mon_control_change', None)
    if dpg.get_value('mon_program_change_active_until') < now:
        dpg.bind_item_theme('mon_program_change', None)
    if dpg.get_value('mon_aftertouch_active_until') < now:
        dpg.bind_item_theme('mon_aftertouch', None)
    if dpg.get_value('mon_pitchwheel_active_until') < now:
        dpg.bind_item_theme('mon_pitchwheel', None)
    if dpg.get_value('mon_sysex_active_until') < now:
        dpg.bind_item_theme('mon_sysex', None)
    if dpg.get_value('mon_quarter_frame_active_until') < now:
        dpg.bind_item_theme('mon_quarter_frame', None)
    if dpg.get_value('mon_songpos_active_until') < now:
        dpg.bind_item_theme('mon_songpos', None)
    if dpg.get_value('mon_song_select_active_until') < now:
        dpg.bind_item_theme('mon_song_select', None)
    if dpg.get_value('mon_tune_request_active_until') < now:
        dpg.bind_item_theme('mon_tune_request', None)
    if dpg.get_value('mon_clock_active_until') < now:
        dpg.bind_item_theme('mon_clock', None)
    if dpg.get_value('mon_start_active_until') < now:
        dpg.bind_item_theme('mon_start', None)
    if dpg.get_value('mon_continue_active_until') < now:
        dpg.bind_item_theme('mon_continue', None)
    if dpg.get_value('mon_stop_active_until') < now:
        dpg.bind_item_theme('mon_stop', None)
    if dpg.get_value("mon_reset_active_until") < now:
        dpg.bind_item_theme('mon_reset', None)


def _clear_probe_data_table():
    dpg.delete_item('probe_data_table', children_only=True, slot=1)
    _init_details_table_data()


def _init_details_table_data():
    # Initial data for reverse scrolling
    with dpg.table_row(parent='probe_data_table', label='probe_data_0'):
        pass


###
#  MAIN PROGRAM
###
if __name__ == '__main__':
    dpg.create_context()

    _init_logger()

    if not DEBUG:
        dpg.configure_app(init_file=INIT_FILENAME)

    ###
    # DEAR PYGUI VALUES
    ###
    with dpg.value_registry():
        dpg.add_string_value(tag='generator_decoded_message', default_value='')
        dpg.add_float_value(tag='blink_duration', default_value=.25)  # seconds
        for channel in range(16):  # Monitoring status
            dpg.add_float_value(tag=f"mon_{channel}_active_until", default_value=0)  # seconds
        dpg.add_float_value(tag='mon_s_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_active_sensing_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_note_off_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_note_on_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_polytouch_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_control_change_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_program_change_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_aftertouch_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_pitchwheel_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_sysex_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_quarter_frame_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_songpos_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_song_select_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_tune_request_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_clock_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_start_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_continue_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_stop_active_until', default_value=0)  # seconds
        dpg.add_float_value(tag='mon_reset_active_until', default_value=0)  # seconds
        # Per standard, consider note-on with velocity set to 0 as note-off
        dpg.add_bool_value(tag='zero_velocity_note_on_is_note_off', default_value=True)

    with dpg.window(
            tag='main_win',
            label="MIDI Explorer",
            width=1920,
            height=1080,
            no_close=True,
            collapsed=False,
    ) as main_win:

        with dpg.menu_bar():
            if DEBUG:
                with dpg.menu(label="Debug"):
                    dpg.add_menu_item(label="Show About", callback=lambda: dpg.show_tool(dpg.mvTool_About))
                    dpg.add_menu_item(label="Show Metrics", callback=lambda: dpg.show_tool(dpg.mvTool_Metrics))
                    dpg.add_menu_item(label="Show Documentation", callback=lambda: dpg.show_tool(dpg.mvTool_Doc))
                    dpg.add_menu_item(label="Show Debug", callback=lambda: dpg.show_tool(dpg.mvTool_Debug))
                    dpg.add_menu_item(label="Show Style Editor", callback=lambda: dpg.show_tool(dpg.mvTool_Style))
                    dpg.add_menu_item(label="Show Font Manager", callback=lambda: dpg.show_tool(dpg.mvTool_Font))
                    dpg.add_menu_item(label="Show Item Registry",
                                      callback=lambda: dpg.show_tool(dpg.mvTool_ItemRegistry))
                    dpg.add_menu_item(label="Show ImGui Demo", callback=lambda: dpg.show_imgui_demo())
                    dpg.add_menu_item(label="Show ImPlot Demo", callback=lambda: dpg.show_implot_demo())
                    dpg.add_menu_item(label="Show Dear PyGui Demo", callback=lambda: show_demo())

            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Save configuration", callback=_save_init)

            with dpg.menu(label="Display"):
                dpg.add_menu_item(label="Toggle Fullscreen (F11)", callback=dpg.toggle_viewport_fullscreen)
                dpg.add_menu_item(label="Toggle Log (F12)", callback=_toggle_log)

            dpg.add_menu_item(label="About")  # TODO

    with dpg.window(
            tag="conn_win",
            label="Connections",
            width=960,
            height=795,
            no_close=True,
            collapsed=False,
            pos=[0, 20]
    ):
        # TODO: connection presets management

        with dpg.menu_bar():
            with dpg.window(label="Refresh MIDI ports", show=False, popup=True) as refresh_midi_modal:
                dpg.add_text("Warning: All links will be removed.")
                dpg.add_separator()
                with dpg.group(horizontal=True):
                    dpg.add_button(label="OK", width=75, callback=_refresh_midi_ports)
                    dpg.add_button(label="Cancel", width=75,
                                   callback=lambda: dpg.configure_item(refresh_midi_modal, show=False))

            dpg.add_menu_item(label="Refresh MIDI ports",
                              callback=lambda: dpg.configure_item(refresh_midi_modal, show=True))

            dpg.add_menu_item(label="Add probe")  # TODO

            # TODO: Add a toggle between input polling and callback modes

        with dpg.node_editor(callback=link_callback,
                             delink_callback=delink_callback) as connections_editor:
            with dpg.node(label="INPUTS",
                          pos=[10, 10]) as inputs_node:
                # Dynamically populated
                with dpg.popup(dpg.last_item()):
                    dpg.add_button(label="Add virtual input")

            with dpg.node(tag='probe_node',
                          label="PROBE",
                          pos=[360, 25]) as probe:
                with dpg.node_attribute(tag='probe_in',
                                        label="In",
                                        attribute_type=dpg.mvNode_Attr_Input,
                                        shape=dpg.mvNode_PinShape_Triangle) as probe_in:
                    dpg.add_text("In")

                with dpg.node_attribute(tag='probe_thru',
                                        label="Thru",
                                        attribute_type=dpg.mvNode_Attr_Output,
                                        shape=dpg.mvNode_PinShape_Triangle) as probe_thru:
                    dpg.add_text("Thru")

            with dpg.node(label="GENERATOR",
                          pos=[360, 125]):
                with dpg.node_attribute(label="Out",
                                        attribute_type=dpg.mvNode_Attr_Output,
                                        shape=dpg.mvNode_PinShape_Triangle) as gen_out:
                    dpg.add_text("Out", indent=2)

            with dpg.node(label="FILTER/TRANSLATOR",
                          pos=[360, 250]):
                with dpg.node_attribute(label="In",
                                        attribute_type=dpg.mvNode_Attr_Input,
                                        shape=dpg.mvNode_PinShape_Triangle):
                    dpg.add_text("In")
                with dpg.node_attribute(label="Out",
                                        attribute_type=dpg.mvNode_Attr_Output,
                                        shape=dpg.mvNode_PinShape_Triangle):
                    dpg.add_text("Out", indent=2)

            with dpg.node(label="OUTPUTS",
                          pos=[610, 10]) as outputs_node:
                # Dynamically populated
                with dpg.popup(dpg.last_item()):
                    dpg.add_button(label="Add virtual output")

    with dpg.window(
            tag='probe_win',
            label="Probe",
            width=960,
            height=695,
            no_close=True,
            collapsed=False,
            pos=[960, 20]
    ) as probe_data:

        with dpg.menu_bar():
            with dpg.menu(label="Settings"):
                dpg.add_slider_float(tag='blink_duration_slider',
                                     label="Persistence (s)",
                                     min_value=0, max_value=0.5, source='blink_duration',
                                     callback=lambda:
                                     dpg.set_value('blink_duration', dpg.get_value('blink_duration_slider')))
                dpg.add_checkbox(label="0 velocity note-on is note-off (default, MIDI specification compliant)",
                                 source='zero_velocity_note_on_is_note_off')

        # Input Activity Monitor
        dpg.add_child_window(tag='act_mon', label="Input activity monitor", height=50, border=False)

        with dpg.table(parent='act_mon', header_row=False, policy=dpg.mvTable_SizingFixedFit):
            dpg.add_table_column(label="Title")
            for channel in range(18):
                dpg.add_table_column()

            with dpg.theme(tag='__red'):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 0, 0))

            with dpg.table_row():
                dpg.add_text("Channels:")
                for channel in range(16):  # Channel messages
                    dpg.add_button(tag=f"mon_{channel}", label=f"{channel + 1}")
                    with dpg.tooltip(dpg.last_item()):
                        dpg.add_text(f"Channel {channel + 1}")
                dpg.add_button(tag='mon_s', label="S")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("System Message")
            with dpg.table_row():
                dpg.add_text("Types:")

                # Channel voice messages (page 9)
                dpg.add_button(tag='mon_note_off', label="OFF ")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Note-Off")
                dpg.add_button(tag='mon_note_on', label=" ON ")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Note-On")
                dpg.add_button(tag='mon_polytouch', label="PKPR")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Poly Key Pressure (Note Aftertouch)")
                dpg.add_button(tag='mon_control_change', label=" CC ")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Control Change")
                dpg.add_button(tag='mon_program_change', label=" PC ")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Program Change")
                dpg.add_button(tag='mon_aftertouch', label="CHPR")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Channel Pressure (Channel Aftertouch)")
                dpg.add_button(tag='mon_pitchwheel', label="PTCH")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Pitch Bend")

                # TODO: Channel mode messages (page 20) (CC 120-127)

                # System common messages (page 27)
                dpg.add_button(tag='mon_quarter_frame', label=" QF ")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("MTC SMPTE Quarter Frame")
                dpg.add_button(tag='mon_songpos', label="SGPS")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Song Position")
                dpg.add_button(tag='mon_song_select', label="SGSL")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Song Select")
                dpg.add_button(tag='mon_tune_request', label=" TR ")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Tune Request")
                # FIXME: mido is missing EOX
                dpg.add_button(tag='mon_eox', label="EOX ")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("End of Exclusive")

                # System real time messages (page 30)
                dpg.add_button(tag='mon_clock', label="CLK ")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Clock")
                dpg.add_button(tag='mon_start', label="STRT")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Start")
                dpg.add_button(tag='mon_continue', label="CTNU")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Continue")
                dpg.add_button(tag='mon_stop', label="STOP")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Stop")
                dpg.add_button(tag='mon_active_sensing', label=" AS ")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Active Sensing")
                dpg.add_button(tag='mon_reset', label="RST ")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Reset")

                # System exclusive messages
                dpg.add_button(tag='mon_sysex', label="SYX ")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("System Exclusive (aka SysEx)")

            with dpg.table_row():
                dpg.add_text("Controllers:")
                # TODO: Control Changes (page 11)
                for controller in range(120):
                    if controller % 16:
                        # TODO: change row
                        pass
                    dpg.add_text("")

            with dpg.table_row():
                dpg.add_text("Channel mode:")
                # TODO: Channel modes (page 20)
                for mode in range(120, 128):
                    dpg.add_text("")

            with dpg.table_row():
                dpg.add_text("System exclusive:")
                # TODO: decode 1 or 3 byte IDs (page 34)
                dpg.add_text("")
                # TODO: decode sample dump standard (page 35)
                # ACK, NAK, Wait, Cancel & EOF
                # TODO: decode device inquiry (page 40)
                # TODO: decode file dump (page 41)
                # TODO: decode midi tuning (page 47)
                # TODO: decode general midi system messages (page 52)
                # TODO: decode MTC full message, user bits and real time cueing (page 53 + dedicated spec)
                # TODO: decode midi show control (page 53 + dedicated spec)
                # TODO: decode notation information (page 54)
                # TODO: decode device control (page 57)
                # TODO: decode MMC (page 58 + dedicated spec)

            with dpg.table_row():
                dpg.add_text("Running status:")
                # FIXME: unimplemented upstream (page A-1)

        dpg.add_child_window(tag='probe_table_container')

        # Details buttons
        # FIXME: separated to not scroll with table child window until table scrolling is supported
        dpg.add_child_window(parent='probe_table_container', tag='act_det_btns', label="Buttons", height=40,
                             border=False)
        with dpg.group(parent='act_det_btns', horizontal=True):
            dpg.add_checkbox(tag='probe_data_table_autoscroll', label="Auto-Scroll", default_value=True)
            dpg.add_button(label="Clear", callback=_clear_probe_data_table)

        # Details
        # FIXME: workaround table scrolling not implemented upstream yet to have static headers
        # dpg.add_child_window(tag='act_det_headers', label="Details headers", height=5, border=False)
        with dpg.table(parent='act_det_btns',
                       tag='probe_data_table_headers',
                       header_row=True,
                       freeze_rows=1,
                       policy=dpg.mvTable_SizingStretchSame):
            dpg.add_table_column(label="Timestamp (ms)")
            dpg.add_table_column(label="Delta (ms)")
            dpg.add_table_column(label="Source")
            dpg.add_table_column(label="Raw Message (HEX)")
            if DEBUG:
                dpg.add_table_column(label="Decoded Message")
            dpg.add_table_column(label="Channel")
            dpg.add_table_column(label="Status")
            dpg.add_table_column(label="Data 1")
            dpg.add_table_column(label="Data 2")

        # TODO: Allow sorting
        # TODO: Show/hide columns
        # TODO: timegraph?

        dpg.add_child_window(parent='probe_table_container', tag='act_det', label="Details", height=525, border=False)
        with dpg.table(parent='act_det',
                       tag='probe_data_table',
                       header_row=False,  # FIXME: True when table scrolling will be implemented upstream
                       freeze_rows=0,  # FIXME: 1 when table scrolling will be implemented upstream
                       policy=dpg.mvTable_SizingStretchSame,
                       # scrollY=True,  # FIXME: Scroll the table instead of the window when available upstream
                       clipper=True):
            dpg.add_table_column(label="Timestamp (ms)")
            dpg.add_table_column(label="Delta (ms)")
            dpg.add_table_column(label="Source")
            dpg.add_table_column(label="Raw Message (HEX)")
            if DEBUG:
                dpg.add_table_column(label="Decoded Message")
            dpg.add_table_column(label="Channel")
            dpg.add_table_column(label="Status")
            dpg.add_table_column(label="Data 1")
            dpg.add_table_column(label="Data 2")

            _init_details_table_data()

    with dpg.window(
            tag='gen_win',
            label="Generator",
            width=960,
            height=100,
            no_close=True,
            collapsed=False,
            pos=[960, 715]
    ) as gen_data:

        message = dpg.add_input_text(label="Raw Message", hint="XXYYZZ (HEX)", hexadecimal=True, callback=_decode)
        dpg.add_input_text(label="Decoded", readonly=True, hint="Automatically decoded raw message",
                           source='generator_decoded_message')
        dpg.add_button(tag="generator_send_button", label="Send", enabled=False)

    _refresh_midi_ports()

    with dpg.handler_registry():
        dpg.add_key_press_handler(key=122, callback=dpg.toggle_viewport_fullscreen)  # Fullscreen on F11
        dpg.add_key_press_handler(key=123, callback=_toggle_log)  # Log on F12

    ###
    # DEAR PYGUI SETUP
    ###
    dpg.create_viewport(title='MIDI Explorer', width=1920, height=1080)

    # Icons must be called before showing viewport
    # TODO: icons
    # dpg.set_viewport_small_icon("path/to/icon.ico")
    # dpg.set_viewport_large_icon("path/to/icon.ico")

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window(main_win, True)

    ###
    # MAIN LOOP
    ###
    while dpg.is_dearpygui_running():  # Replaces dpg.start_dearpygui()
        _update_blink_status()

        ###
        # MIDI Data receive & handling: Polling mode
        ###
        # FIXME: Use callback mode to avoid framerate dependency.
        # Shorter MIDI message (1-byte) is 320us.
        # 60FPS frame time is 16.7ms
        # This amounts to up to 53 MIDI bytes per frame (52.17)!
        probe_in_user_data = dpg.get_item_user_data(probe_in)
        if probe_in_user_data:
            # logger.log_debug(f"Probe input has user data: {probe_in_user_data}")
            while True:
                timestamp = time.time()
                midi_data = probe_in_user_data["IN"].poll()
                if not midi_data:  # Could also use iter_pending() instead.
                    break
                logger.log_debug(f"Received MIDI data from probe input: {midi_data}")
                probe_thru_user_data = dpg.get_item_user_data(probe_thru)
                if probe_thru_user_data:
                    # logger.log_debug(f"Probe thru has user data: {probe_thru_user_data}")
                    logger.log_debug(f"Sending MIDI data to probe thru")
                    probe_thru_user_data["OUT"].send(midi_data)
                _add_probe_data(timestamp=timestamp,
                                source=probe_in,
                                data=midi_data)

        dpg.render_dearpygui_frame()

    dpg.destroy_context()
