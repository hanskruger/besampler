from collections import namedtuple
from functools import reduce
import numpy as np
import datetime
import re, os
import wave
from pydub import AudioSegment
from pathlib import Path



class Clock():
    def __init__(self, hz, offset_ms = 0):
        self._hz = hz
        self._offset = float(offset) # number of samples.

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
