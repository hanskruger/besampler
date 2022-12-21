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
from .measure import match_pause
from .player import ProgEntry

def match_head_on_1(inp):
    if inp and "|" == inp[0]:
        return True
    return False

def normalize_beat(inp):
    return inp

def match_pattern(pattern, staff_line, idx, head_index, time_signature, on_beat_1 ):
    '''
    Given a pattern (array of strings), return true, if this pattern matches to the staff line
    '''
    if ((len(staff_line) - idx) < len(pattern)):
        return False

    if (on_beat_1 and head_index != (idx % time_signature.pulses)):
        # Check for paterns, that need to start on the first beat of a bar 
        return False

    for i in range(len(pattern)):
        if pattern[i] != staff_line[i + idx]:
            return False
    return True

def parse_pattern(pattern):
    on_beat_1 = match_head_on_1(pattern)
    beats   = re.split("\\s+", pattern.strip(" \t|"))
    return beats, on_beat_1

class Pattern():
    def __init__(self, pattern):
        self._pattern = pattern
        self._pattern, self._on_beat_1  = parse_pattern(pattern)
        self._samples = []
        self._aliases = []

    def add_samples(self, *samples):
        self._samples.extend(samples)
        return self

    def match(self, staff_line, idx, head_index = 0, time_signature = TimeSignature()):
        '''
        Match for a given pattern.
        head_index is the index, taht marks the first beat in the bar. You can use it
        to match patterns, taht need to start at a given position in the bar.
        '''
        if match_pattern(self._pattern, staff_line, idx, head_index,time_signature, self._on_beat_1):
            return True
        for alias in self._aliases:
            if match_pattern(alias, staff_line, idx, head_index,time_signature, self._on_beat_1):
                return True
        return False 
    
    def alias(self, pattern):
        self._aliases.append( parse_pattern(pattern)[0] )
        return self

    def __len__(self):
        '''
        Return the length in beatzs for this pattern"

        >>> len(Pattern("XxLr X.X. r..."))
        3
        '''
        return len(self._pattern)

    def __str__(self):
        return self._pattern

    def __repr__(self):
        return f"<Pattern {self} at 0x{id(self):x}>"
    
    def apply(self, idx, programm, score, staff, staffline, artist, repeat_index  ):
        return self.sample(repeat_index).apply(self, idx, programm, score, staff, staffline, artist, repeat_index )

    def sample(self, repeat_index = 0):
        return self._samples[ repeat_index % len(self._samples) ]

