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

class Pattern():
    def __init__(self, pattern):
        self._pattern = pattern
        self._beats   = re.split("\\s+", self._pattern)
        self._samples = []

    def add_samples(self, *samples):
        self._samples.extend(samples)
        pass


    def match(self, staff_line, idx, head_index = 0, time_signature = TimeSignature()):
        '''
        Match for a given pattern.
        head_index is the index, taht marks the first beat in the bar. You can use it
        to match patterns, taht need to start at a given position in the bar.
        '''
        # todo: Add match for patterns that begin on start of a bar.
        if ((len(staff_line) - idx) < len(self._beats)):
            #print("XX ", idx, len(staff_line), len(self._beats), self._pattern)
            #this pattern is longer than than the number of measures left.
            return False
        for i in range(len(self._beats)):
            if self._beats[i] != staff_line[i + idx]:
                return False
        return True

    def __len__(self):
        '''
        Return the length in beatzs for this pattern"

        >>> len(Pattern("XxLr X.X. r..."))
        3
        '''
        return len(self._beats)

    def __str__(self):
        return self._pattern

    def __repr__(self):
        return f"<Pattern {self} at 0x{id(self):x}>"

    def sample(self, repeat_index = 0):
        return self._samples[ repeat_index % len(self._samples) ]

