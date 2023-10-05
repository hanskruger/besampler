from collections import namedtuple
from functools import reduce
import numpy as np
import datetime
import re, os
import wave
from pydub import AudioSegment
from pathlib import Path
from functools import total_ordering
import re
from locale import atof
import functools
import random
import logging

from .wavefile import WaveFile
from .pattern import Pattern, parse_pattern
from .sample_builder import SampleBuilder
from .pattern import reciept_parser

class Instrument():
    pass
    def __init__(self, name, bpm = 120, auto_pattern = False):
        self._name = name
        self._patterns = {}
        self._bpm = bpm
        self._auto_pattern = auto_pattern
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
    
    @property
    def auto_pattern(self):
        return self._auto_pattern

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

    def build_pattern(self, pattern, reciept, bpm, frame_rate, variations = 13, aliases = []):
        '''
        Build an new pattern based on the given reciept
        '''
        if isinstance(reciept, str):
            reciept = [ reciept, ]
            

        logging.debug(f'Adding cliche "{pattern}" for instrument {self.name}.')
        pattern = self.add_pattern(pattern).random(True)
        for alias in aliases:
            logging.debug(f'Adding alias "{alias}" to cliche "{pattern}" for instrument {self.name}.')
            pattern.alias(alias)
        # 1. pass: build the smaple!
        prog = []
        for pulse in range(len(reciept)):
            for rec in reciept_parser(reciept[pulse]):
                pat = parse_pattern(rec.pattern)
                shift = rec.shift
                # TODO replce next line with best match function
                patterns = sorted(
                        filter(
                            lambda x: x.pattern == pat.pattern and x.on_beat_1 == pat.on_beat_1 and not x.cliche,
                            self._patterns.values()),  key=lambda x: x.score)
                if (not patterns):
                    raise RuntimeError(f"Could not find a pattern for \"{pat}\" to build cliche \"{pattern}\" for instrument {instrument}")
                # if we have more than one pattern, something is wrong! Take the first one.
                pat = patterns[0]
                prog.append( (pat, shift, rec.gain, pulse) )
        print(pattern, reciept, prog)

        variations = min(variations, functools.reduce(lambda x,y: x*y, map( lambda x: len(x[0].samples), prog)))
        if variations > 1:
            logging.debug(f"Adding {variations} random variations of this cliche.")
        for i in range(variations):
            sb = SampleBuilder(bpm, frame_rate)
            for (pat, shift, gain, pulse) in prog:
                sb.add_subsample( random.choice( pat.samples ), shift, gain, pulse )
            # 2. Add the pattern!
            pattern.add_samples(sb.build())
        return pattern


