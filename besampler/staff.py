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
from .measure import Measure

@total_ordering
class Staff():
    def __init__(self, name, lines = 5, key = "Violin"):
        self._name = name
        pass

    def __call__(self, measure):
        RetVal = namedtuple("RetVal",["measure","staff"])
        return RetVal(Measure.parse(measure, strict=True), self)

    def __hash__(self):
        return hash(self._name)

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self._name
    def __repr__(self):
        return f"<staff {self._name} at 0x{id(self):x}>"

    def __hash__(self):
        return hash(f"Staff<{self._name}>")

    def __eq__(self, other):
        '''
        >>> Staff("a") == Staff("a")
        True
        >>> Staff("a") == Staff("b")
        False
        '''
        return isinstance(other, Staff) and self._name == other.name

    def __lt__(self, other):
        '''
        >>> Staff("a") < Staff("a")
        False
        >>> Staff("a") < Staff("b")
        True
        >>> Staff("b") < Staff("a")
        False
        >>> Staff("b") <= Staff("a")
        False
        '''
        return isinstance(other, Staff) and self._name < other.name
