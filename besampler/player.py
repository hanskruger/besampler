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

class InstrumentSettings():
    def __init__(self):
        pass

    def pan(self, position):
        return self

    def delay(self, ms):
        return self

    def gain(self, dbfs):
        return self

class Player():
    def __init__(self, bpm = 135):
        self._bpm = bpm
        self._freq = 48000;
        self._artist = {}
        self._out_dir = Path(".") 

    def __synth_measure(self, m):
        pass

    def add_artist(self, name, staff, instrument):
        Artist = namedtuple("Artist",["name", "staff","settings", "instrument"])
        settings = InstrumentSettings()
        self._artist.setdefault(staff, []).append(Artist(name, staff, settings, instrument))
        return settings

    def _compile_instrument(self, artist, staff, score):
        Prog      = namedtuple("Prog",["programm", ])
        ProgEntry = namedtuple("ProgEntry",["pattern", "repeat_index", "staff_index"])
        print(f"Generating audio track for artist {artist.name}({artist.instrument.name}), staff {staff}.")
        head_index = 0;
        instrument = artist.instrument
        measures = list(score.measures(staff))
        staff_line = list(reduce(lambda a,b: a+b,  map(lambda x: x.measure.notes, measures)))
        prog = []
        print( staff_line)

        idx, mcount = 0, len(staff_line)
        while idx < mcount:
            # Find patterns, that best match to this measure
            # this sdarch algorithm sohould be improved later onl. We need a traveling salesman search over
            # the combination of "paths". And then we evaluate the "length" of the path and choose the best one.
            # The best path in this ase is the one,  that need less patterns to complete.
            patterns = sorted(filter(lambda x: x.match(staff_line, idx, head_index = head_index, time_signature = score.time_signature), iter(instrument)), key = len)

            if (not patterns):
                if ("...." == staff_line[idx] or "-" == staff_line[idx]): # skip pause
                    idx += 1
                    continue
                if ("%" == staff_line[idx]): # handle measure repeat
                    if head_index != (idx % 4):
                        raise RuntimeError(f"Repeat must be at beginning of the bar.")
                    # todo: handle repeat of last n beats
                    raise RuntimeError(f"Repeat not supported yet.")
                    pass
                raise RuntimeError(f"No pattern found for {staff_line[idx]}(idx).")

            # choose most appropriate patter
            pat = patterns[0]
            repeat_index = 0 if (not prog or  prog[-1].pattern != pat) else prog[-1].repeat_index + 1
            prog.append( ProgEntry(pat, repeat_index, idx) )
            idx = idx + len(pat)

        # start synthesizing the sound file.

        return Prog(prog)

    def _synth_instrument(self, prog, artis, score):
        lenght_ms      = 60000.0 * score.length * score.time_signature.pulses / self._bpm
        lenght_samples = lenght_ms * self._freq / 1000.0
        instrument = artis.instrument
        filename = self._out_dir / Path( f"{instrument.name}_{artis.name}.wav")
        print(filename)


        wav = WaveFile.silence(lenght_ms, self._freq)

        for p in prog.programm:
            offset =  1000.0 * p.staff_index * 60.0 / self._bpm
            print(offset, p.pattern.sample(p.repeat_index).wave)
            wav.overlay(p.pattern.sample(p.repeat_index).wave , offset=offset)


        wav.export(filename)
        return filename

    def synthesize(self, score, staff = None):

        # pass 1: detect all stafflines
        staffs = []
        for m in score.measures():
            for s in m:
                staffs.append(s.staff)
        staffs = set(staffs)

        lenght_ms      = 60000.0 * score.length * score.time_signature.pulses / self._bpm
        lenght_samples = lenght_ms *  self._freq / 1000
        print(f"Total length of this score is {score.length * score.time_signature.pulses} beats, {lenght_ms/1000}s")

        instruments = []

        # pass 2: Check for instrumetns for all staff lines
        for s in staffs:
            if s.name not in self._artist.keys():
                print(f"No artist given for staff {s}.")
                continue
            for i in self._artist[s.name]:
                # pass 3: For each staff line and isntrument, generate the wave file
                prog = self._compile_instrument(i, s, score)
                self._synth_instrument(prog, i, score)
                print(prog.programm)

                # pass 4: Apply PAN, gain, deplay etc. for each instrument

        # pass 5: Apply dynamics for each instrument or instrument groups

        # pass 6: Merge all wave files into one



    def play(self, score):
        pass


