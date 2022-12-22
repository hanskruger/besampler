from collections import namedtuple
from functools import reduce
import numpy as np
import datetime
import re, os
import wave
import logging
from pydub import AudioSegment
from pathlib import Path

from .utils import TimeSignature, Clock
from .staff import Staff

class Score():
    def __init__(self, time_signature = TimeSignature()):
        self._score = []
        self._time_signature = time_signature

    @property
    def time_signature(self):
        return self._time_signature

    def add_staff(self, staff):
        return staff

        
    @property
    def staffs(self):
        '''
        Return the list osf staffs/Instruments in the score
        '''
        staffs = []
        for m in self.measures():
            for s in m:
                staffs.append(s.staff)
        return list( set(staffs))

    def loop(self, num):
        new_score = [] 
        for i in range(num):
            new_score.extend(self._score)
        self._score = new_score
        return self 


    def add_count_in(self, pattern = "x x x x", staff = Staff("Count In")):
        '''
        Prepends a bar with a count in.
        '''
        self._score.insert(0, [ staff(pattern), ])
        return self 
    
    def add_click(self,  pattern = "X x x x", staff = Staff("Click")):
        '''
        Add a extra staff line with a click.
        '''
        entry = staff(pattern)
        for m in self._score:
            m.append(entry)
        return self

    def add_measure(self, *instruments):
        instruments[0].measure
        instruments[0].staff
        self._score.append(list(instruments))
        return self 

    @property
    def length(self):
        '''Return the length in bars'''
        return len(self._score)

    def measures(self, staff = None):
        if None is staff:
            for m in self._score:
                yield m
            return

        for m in self._score:
            found = False
            for e in m:
                if e.staff == staff:
                    found = True
                    yield e
            if not found:
                yield None


    def add_staff_line(self, lines, line = 0):
        '''
        Each staff line is composed of multiple lines all of the same length. Teh bar lines must
        be at the same position. is prepended by the name of the instruament.
        '''
        # Do some checks: All lines must have the same length and the bars must be a t the same location.
        if (1 != len(list(set(map(len, lines))))):
            raise RuntimeError(f"Error while parsing line {line}: All staff lines MUST have the same length (except for trailing whitespaces)")
            pass

        instruments = list(map(lambda x: Staff(x.split("|", 1)[0].strip()), lines))
        staffs = {}
        for instrument, measures in zip(instruments, list(map(lambda x: x.split("|")[1:-1], lines))):
            staffs[ instrument ] = measures

        if (1 != len(set(map(len, staffs.values())))):
            raise RuntimeError(f"Error while parsing line {line}: Within a staff line, each line must have the same amount of bars.")
        bar_count = len(list(staffs.values())[0])

        # transpose our input line.
        for bar in  range(0, bar_count):
            self.add_measure(*list(map(lambda x: x(staffs[x][bar], line=line), instruments)))

    @staticmethod
    def from_file(filename):
        score = Score()

        with open(filename, "r") as f:
            staffline = []
            lineno = 0
            for line in map(lambda x: x.strip(), f.readlines()):
                lineno = lineno + 1
                if(not line):
                    if(staffline):
                        score.add_staff_line(staffline, lineno)
                        staffline = []
                    continue
                #print(line)
                measures = line.split("|")
                if (len(measures)  > 1):
                    staffline.append(line)
                    # parse staffline
                    pass
        return score



