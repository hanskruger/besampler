from collections import namedtuple
from functools import reduce
import numpy as np
import datetime
import re, os
import wave
from pydub import AudioSegment
from pathlib import Path
from functools import total_ordering

from .utils import TimeSignature, Clock
from .wavefile import WaveFile
from .pattern import match_pause, match_repeat

def ms(value):
    return datetime.timedelta(milliseconds=int(value))


class Measure():
    def __init__(self, notes, time_signature = TimeSignature()):
        self._time_signature = time_signature
        self._notes = notes
        pass
        

    def parse(inp, time_signature = TimeSignature(), strict = True, line = 0):
        '''
        If strict is true, parsing will fail, if wrong number of beats are given.
        '''
        inp_orig = inp
       

        if (match_repeat(inp)):
            raise RuntimeError(f"Error parsing line {line}: Parsing repeat not supported yet.")
        if (m := match_pause(inp)): # empty measures are encoded as pause.
            inp = "".join(map(lambda x: "- ", range(0,time_signature.pulses)))

        inp = inp.strip("\t ")
        inp = re.split("\\s+", inp)

        if strict and len(inp) != time_signature.pulses:
            raise RuntimeError(f"Error parsing '{inp_orig}', line {line}: Number of pulses in measure must be exactly {time_signature.pulses}.")

        return Measure(inp, time_signature)

    @property
    def notes(self):
        return self._notes

    def parse_line(inp):
        '''
        Parse a whole line, with prefix and trailing text and mutiple bars sepparated by |
        '''
        return [ Measure.parse(inp)  ]

    def __str__(self):
        return " ".join(self._notes)

    def __repr__(self):
        return f"<Instrument {self} at 0x{id(self):x}>"


