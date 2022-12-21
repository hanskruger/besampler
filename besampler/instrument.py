from collections import namedtuple
from functools import reduce
import numpy as np
import datetime
import re, os
import wave
from pydub import AudioSegment
from pathlib import Path
from functools import total_ordering

from .wavefile import WaveFile
from .pattern import Pattern

class Instrument():
    pass
    def __init__(self, name, bpm = 120):
        self._name = name
        self._patterns = {}
        self._bpm = bpm
        pass

    def add_pattern(self, *patterns):
        '''
        Add a given pattern to this instrument
        '''
        pat = Pattern(patterns[0])

        # todo, need to check, that all patterns have the same lenght in beats!
        for p in patterns:
            self._patterns[p] = pat
        return pat


    def __iter__(self):
        return iter(self._patterns.values())

    def to_staff():
        return Staff(self._name)

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self._name
    def __repr__(self):
        return f"<Instrument {self._name} at 0x{id(self):x}>"
    
    def __hash__(self):
        return hash(f"Instrument<{self._name}>")

    def __eq__(self, other):
        return isinstance(other, Instrument) and self._name == other.name

    def __lt__(self, other):
        return isinstance(other, Instrument) and self._name < other.name
