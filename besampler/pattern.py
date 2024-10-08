from collections import namedtuple
from functools import reduce
import numpy as np
import datetime
import re, os
import wave
import random
from pydub import AudioSegment
from pathlib import Path
from functools import total_ordering
from locale import atof

from .utils import TimeSignature, Clock

def match_pause(s):
    '''
    Returns true, is a beat of only pause is matched.
    >>> match_pause("") is not None
    True
    >>> match_pause("     ") is not None
    True
    >>> match_pause(".") is not None
    True
    >>> match_pause("..") is not None
    True
    >>> match_pause("....") is not None
    True
    >>> match_pause("-") is not None
    True
    >>> match_pause("-x-") is not None
    False
    >>> match_pause(".X..") is not None
    False
    '''
   
    # hard match commom pauise patterns to speed up detection
    if ("-" == s or "...." == s or "..." == s):
        return True
    PAUSE_PATTERN = "^\\s*(\\.+|-)\\s*$"
    if (not s or "" == s.strip()):
        return "-"

    if (m := re.match(PAUSE_PATTERN, s)):
        return m.group(1)
    return None

def match_repeat(s):
    '''
    Returns true, is a beat of only pause is matched.
    
    >>> match_repeat(" % ") is not None
    True
    >>> match_repeat(" %% ") is None
    True
    '''

    PATTERN = "^\\s*(%)\\s*$"
    
    if (m := re.match(PATTERN, s)):
        return m.group(1)
    return None

def match_head_on_1(inp):
    if inp and "|" == inp[0]:
        return True
    return False

def normalize_beat(inp):
    return inp

TONE_PATTERN = "[a-zA-B0-9]"

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

def parse_tone(tone):
    if not tone:
        return ""
    if (match_pause(tone)):
        return ""
    if (m := re.match(f"^({TONE_PATTERN})\\.+$", tone)):
        return m.group(1)
    return tone

def parse_staffline():
    pass

def parse_measure():
    pass

def parse_pattern(pattern):
    RetVal    = namedtuple("PatternParsing",["pattern", "on_beat_1" ])
    on_beat_1 = match_head_on_1(pattern)
    beats   = list(map(parse_tone, re.split("\\s+", pattern.strip(" \t|"))))

    return RetVal(beats, on_beat_1)
    
def reciept_maker(pattern):
    prog = list()
    # First: compute a program
    for i in range(0, len(pattern)):
        if match_pause(pattern[i]):
            continue
        tp = "."*i + "x" + "."*(len(pattern)-i-1)
        prog.append( ( pattern[i], tp ) )
    if (not prog):
        return "-" # return pause!
    return ";".join(map(lambda x: x[0] + ":" +  x[1], prog))

def reciept_parser(reciept):
    ProgEntry = namedtuple("ProgEntry",["pattern", "shift", "gain" ])
    prog = []
    if not reciept:
        return prog
    for rec in reciept.split(";"):
        pat, shift = rec.split(":")[0:2]
        gain = 0.0
        if (m := re.match(".*:gain=([+-]?[.,0-9]+)", rec)):
            gain = atof(m.group(1))
        #pat = parse_pattern(pat)
        shift = str(shift)
        prog.append( ProgEntry(pat, shift, gain) )
    return prog


class Pattern():
    def __init__(self, pattern, cliche = False, random = False):
        self._pattern = pattern
        self._pattern, self._on_beat_1  = parse_pattern(pattern)
        self._samples = []
        self._aliases = []
        self._cliche  = cliche
        self._random = random

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

    def alias(self, *patterns):
        for pattern in patterns:
            self._aliases.append( parse_pattern(pattern).pattern )
        return self
   
    def random(self, *value):
        if (len(value)):
            self._random = True if value[0] else False
            return self
        return self._random

    @property
    def pattern(self):
        return self._pattern
    @property
    def on_beat_1(self):
        return self._on_beat_1

    @property
    def score(self):
        '''
        Returns the score of this pattern. The lower the score, the better it is. 
        '''
        #returns a negative number so we don't need to reverse sort function. Taht way, higher score will be ordered first.
        #So the biggest the number the best.
        return -len(self)

    @property
    def cliche(self):
        return self._cliche

    def __len__(self):
        '''
        Return the length in beatzs for this pattern"

        >>> len(Pattern("XxLr X.X. r..."))
        3
        '''
        return len(self._pattern)

    def __str__(self):
        return str(" ".join(self._pattern))

    def __repr__(self):
        return f"<Pattern {self} at 0x{id(self):x}>"
    
    def apply(self, idx, programm, score, staff, staffline, artist, repeat_index  ):
        return self.sample(repeat_index).apply(self, idx, programm, score, staff, staffline, artist, repeat_index )

    def sample(self, repeat_index = 0):
        if self._random:
            return random.choice(self._samples)
        return self._samples[ repeat_index % len(self._samples) ]
    
    @property
    def samples(self):
        return list( self._samples )


