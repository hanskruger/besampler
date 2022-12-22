from collections import namedtuple
from functools import reduce
import numpy as np
import datetime
import re, os
import wave
from pydub import AudioSegment
from pathlib import Path
from math import floor
import hashlib
import mmap

def sha256sum(filename):
    h  = hashlib.sha256()
    with open(filename, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ) as mm:
            h.update(mm)
    return h.hexdigest() 



class Clock():
    def __init__(self, bpm, frame_rate = 48000, offset_ms = 0):
        self._hz = frame_rate
        self._bpm = bpm
        self._offset_ms = float(offset_ms) # number of samples.

    def __add__(self, b):
        if isinstance(b, Clock):
            if b._hz == self._hz:
                return Clock(self._hz, self._offset + b._offset)
            b = b.to_ms()
        if isinstance(b, datetime.timedelta):
            return Clock(self._hz, self._offset + b.total_seconds() * self._hz)
        if isinstance(b, int) or isinstance(b, float):
            return Clock(self._hz, self._offset + b)
        raise RuntimeError(f"Unsupported type {b.__class__}.")

    def pulse(self, idx, shift = None):
        '''
        Return the offset in milli seconds for a given pulse. Start counting on with 0!

        >>> Clock(60).pulse(60)
        60000.0
        >>> Clock(120).pulse(60)
        30000.0
        >>> Clock(60).pulse(0,".x")
        500.0
        >>> Clock(60).pulse(0,"..x.")
        500.0
        >>> Clock(60).pulse(0,".x..")
        250.0
        >>> Clock(60).pulse(0,"...x")
        750.0
        >>> Clock(60).pulse(0,"x...")
        0.0
        >>> floor(Clock(60).pulse(0,"..x"))
        666
        >>> floor(Clock(60).pulse(1,"..x"))
        1666
        '''
        offset =  self._offset_ms + 1000.0 * idx * 60.0 / self._bpm
        if not shift:
            return offset

        PATTERN = "^(\\.*)x(\\.*)$"
        if (m := re.match(PATTERN, shift)):
            beat_lentgh = 60.0 * 1000.0 / self._bpm
            pos = float(len(m.group(1)))
            tot = float(len(shift))
            return offset + beat_lentgh * pos/tot 
        else:
            raise RuntimeError("shift inidactor must consost of dots (.) with one x only.")

    @property
    def pulse_length_ms(self):
        return 60.0 * 1000.0 / self._bpm

    def to_ms(self):
        return datetime.timedelta(milliseconds= int(self._offset/self._hz))

    def index(self):
        return int(0)

class TimeSignature():
    def __init__(self, pulses = 4, note_value = 4):
        self._pulses = 4
        self._note_value = 4

    @property
    def pulses(self):
        return self._pulses

    @property
    def note_value(self):
        return self._note_value

    def fill_bar(self, b):
        return list(map(lambda x: "-", range(0, self._pulses)))
