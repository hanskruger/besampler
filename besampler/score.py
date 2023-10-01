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

StaffLineMatch = namedtuple("StaffLineMatch",["line", "instrument", "staff_line", "tail" ])

def _parse_playset(inp):
    '''
    >>> _parse_playset("1-4")
    [0, 1, 2, 3]
    >>> _parse_playset("1-3,1-4")
    [0, 1, 2, 0, 1, 2, 3]
    >>> _parse_playset("1-3,1-4,4")
    [0, 1, 2, 0, 1, 2, 3, 3]
    '''
    idx = []
    for c in inp.split(","):
        if c.isdecimal():
            idx.append(int(c) - 1)
        elif "-" in c:
            c1 = c.split("-")
            if len(c1) != 2:
                raise RuntimeError("'{c}' is not a valid repeat notation.")
            idx.extend( range( int(c1[0]) - 1, int(c1[1])))
    return idx
 
class Score():
    def __init__(self, time_signature = TimeSignature()):
        self._score = []
        self._time_signature = time_signature
        self._playset = None
        self._patterns = {}

    @property
    def time_signature(self):
        return self._time_signature

    def add_staff(self, staff):
        return staff

    @property
    def patterns(self):
        '''
        REturn teh set of scpore individual patterns
        '''
        return self._patterns
        
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
        idx = self._idx()
        for i in range(num):
            new_score.extend(idx)
        return self 

    def add_count_in(self, pattern = "x x x x", staff = Staff("Count In")):
        '''
        Prepends a bar with a count in.
        '''
        self._score.insert(0, [ staff(pattern), ])
        self._playset = [0,] +  list(map(lambda x: x + 1, self._playset))
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
        return len(self._idx())

    def playset(self, inp):
        self._playset = _parse_playset(inp)
        return self

    def _idx(self):
        if not self._playset:
            return list(range(0, len(self._score)))
        return self._playset

    def measures(self, staff = None):
        idx = self._idx()

        if None is staff:
            for m in idx: 
                yield self._score[m]
            return

        for m in idx:
            found = False
            for e in self._score[m]:
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

        def parse_instrument_name(inp):
            if inp[0] == "%": # in Latex, we ignore the '%' so we can have hidden 
                return inp[1:]
            return inp

        instruments = list(map(lambda x: Staff(parse_instrument_name(x.split("|", 1)[0].strip())), lines))
        staffs = {}
        for instrument, measures in zip(instruments, list(map(lambda x: x.split("|")[1:-1], lines))):
            staffs[ instrument ] = measures

        if (1 != len(set(map(len, staffs.values())))):
            raise RuntimeError(f"Error while parsing line {line}: Within a staff line, each line must have the same amount of bars.")
        bar_count = len(list(staffs.values())[0])

        # transpose our input line.
        for bar in  range(0, bar_count):
            self.add_measure(*list(map(lambda x: x(staffs[x][bar], line=line), instruments)))
 
    def match_latex(self, s, line_no = 0):
        '''
        Match for Latex lines  

        '''
        latex_regex = "(%?\w[\d\s\w]{1,15})&([&a-zA-Z0-9\s\.\/]+)\\\\(.*)"
        m = re.match(latex_regex, s)
        if not m:
            return None
        staff = m.group(2).split("&")
        if (len(staff) % self._time_signature.pulses) != 0:
            raise RuntimeError(f"Staff line in line {line_no} need a multiple of {self._time_signature.pulses} entries.")
        #regroup the staff line in tuples of self._time_signature.pulses
        norm_staff_string = f"{m.group(1)}|";
        for i in range(0, int(len(staff)/self._time_signature.pulses)):
            norm_staff_string = norm_staff_string + " ".join( staff[ i * self._time_signature.pulses : (i+1) * self._time_signature.pulses ]) + "|"
        # Normalize the staff string for further processing
        # first schek, that we have a multiple of beats per measure in thhis staff line
        return StaffLineMatch(s, m.group(1).strip(), norm_staff_string, m.group(3))

    @staticmethod
    def match_text(s, line_no):
        # TODO!
        return StaffLineMatch(s, None, s, None)
        pass

    @staticmethod
    def from_file(filename, mode= "TXT"):
        score = Score()

        # latex regex for staff line:
        txt_regex   = ""

        with open(filename, "r") as f:
            staffline = []
            lineno = 0
            for line in map(lambda x: x.strip(), f.readlines()):
                lineno = lineno + 1
                if (line and line[0] == "#"):
                    continue
                if(not line):
                    if(staffline):
                        score.add_staff_line(staffline, lineno)
                        staffline = []
                    continue
                
                # look for playlist
                if (m := re.match(".*%\s*playlist(\[(\w+)\])?: ([-x,0-9]+)", line)):
                    if not m.group(3):
                        logging.warning(f'Empty playlist in line {lineno}.')
                        continue
                    if not m.group(2): # default playlist
                        logging.debug(f'Found playlist in line {lineno}: {m.group(3)}')
                        score.playset(m.group(3))
                    if m.group(2):
                        logging.warning(f'Alternative playlist {m.group(2)} (line no {lineno}) not supported.')

                    continue
                # todo add capability to add score specific samples.
                if (m := re.match("^\s*%\s*pattern\[(\w+)]\s*:\s*(.*)$", line)):
                    score._patterns.setdefault(m.group(1), []).append( m.group(2).split("=",1))

                m = score.match_latex(line, lineno) if mode == "TEX" else score.match_text(line, lineno)

                if (not m):
                    continue

                measures = m.staff_line.split("|")
                if (len(measures)  > 3):
                    staffline.append(m.staff_line)
                    # parse staffline
                    pass
        return score



