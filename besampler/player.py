from collections import namedtuple
from functools import reduce
import numpy as np
import datetime
import re, os
import wave
import logging
from pydub import AudioSegment
from pathlib import Path
from functools import total_ordering
from math import ceil

from .wavefile import WaveFile
from .measure  import match_pause, match_repeat
from .utils    import Clock

class InstrumentSettings():
    def __init__(self, pan = 0, delay_ms = 0, gain_dbfs = 0.0):
        self._pan = pan
        self._delay_ms = delay_ms
        self._gain = gain_dbfs
        pass

    @property
    def gain(self):
        return self._gain
    @property
    def pan(self):
        return self._pan
    @property
    def delay_ms(self):
        return self._delay_ms

    def set_pan(self, pan):
        self._pan = pan
        return self

    def set_delay(self, delay_ms):
        self._delay_ms = delay_ms
        return self

    def set_gain(self, gain_dbfs):
        self._gain = gain_dbfs
        return self

class Player():
    def __init__(self, bpm = 135):
        self._bpm = bpm
        self._freq = 48000;
        self._artist = {}
        self._click  = None  
        self._out_dir = Path(".") 

    def __synth_measure(self, m):
        pass


    def add_artist(self, name, staff, instrument, setting = InstrumentSettings()):
        Artist = namedtuple("Artist",["name", "staff","settings", "instrument"])
        self._artist.setdefault(staff, []).append(Artist(name, staff, setting, instrument))
        return setting

    def _compile_artist(self, artist, staff, score):
        Prog      = namedtuple("Prog",["programm", ])
        ProgEntry = namedtuple("ProgEntry",["pattern", "repeat_index", "staff_index"])
        logging.info(f"Generating audio track for artist {artist.name}({artist.instrument.name}), staff {staff}.")
        head_index = 0;
        ONE_BAR_PAUSE = score.time_signature.fill_bar("-") 
        instrument = artist.instrument
        measures = list(score.measures(staff))
        #print(staff, measures)
        staff_line = list(reduce(lambda a,b: a+b,  map(lambda x: x.measure.notes if x else ONE_BAR_PAUSE, measures)))
        prog = []
        #print(staff, staff_line)

        idx, mcount = 0, len(staff_line)
        while idx < mcount:
            # Find patterns, that best match to this measure
            # this sdarch algorithm sohould be improved later onl. We need a traveling salesman search over
            # the combination of "paths". And then we evaluate the "length" of the path and choose the best one.
            # The best path in this ase is the one,  that need less patterns to complete.
            patterns = sorted(filter(lambda x: x.match(staff_line, idx, head_index = head_index, time_signature = score.time_signature), iter(instrument)), key = len, reverse = True)

            if (not patterns):
                if (match_pause(staff_line[idx])): # skip pause
                    idx += 1
                    continue
                if ("%" == staff_line[idx]): # handle measure repeat
                    if head_index != (idx % 4):
                        raise RuntimeError(f"Repeat must be at beginning of the bar.")
                    # todo: handle repeat of last n beats
                    raise RuntimeError(f"Repeat not supported yet.")
                    pass
                if(True):
                    logging.warning(f"No pattern found for {staff_line[idx]}(bar {ceil(idx / score.time_signature.pulses)}) for instrument {artist.instrument.name}.")
                    idx += 1
                    continue
                else:
                    raise RuntimeError(f"No pattern found for {staff_line[idx]}({idx}).")

            # choose most appropriate patter
            pat = patterns[0]
            repeat_index = 0 if (not prog or  prog[-1].pattern != pat) else prog[-1].repeat_index + 1
            prog.append( ProgEntry(pat, repeat_index, idx) )
            idx = idx + len(pat)

        # start synthesizing the sound file.

        return Prog(prog)

    def _synth_artist(self, prog, artis, score):
        clk = Clock(self._bpm, frame_rate=self._freq, offset_ms=0)

        lenght_ms      = 60000.0 * score.length * score.time_signature.pulses / self._bpm
        lenght_samples = lenght_ms * self._freq / 1000.0
        instrument = artis.instrument
        filename = self._out_dir / Path( f"{instrument.name}_{artis.name}.wav")
        logging.info(f"Writing track for artist {instrument.name}/{artis.name} to {filename}.")

        wav = WaveFile.silence(lenght_ms, self._freq)

        for p in prog.programm:
            offset =  clk.pulse( p.staff_index )
            #print(offset, p.pattern.sample(p.repeat_index).wave)
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
        logging.info(f"Total length of this score is {score.length * score.time_signature.pulses} beats, {lenght_ms/1000}s")

        instruments = []


        # pass 2: Check for instrumetns for all staff lines
        for s in staffs:
            if s.name not in self._artist.keys():
                logging.warning(f"No artist given for staff {s}.")
                continue
            for i in self._artist[s.name]:
                # pass 3: For each staff line and isntrument, generate the wave file
                prog = self._compile_artist(i, s, score)
                self._synth_artist(prog, i, score)
                #print(prog.programm)

                # pass 4: Apply PAN, gain, deplay etc. for each instrument



        # generte count-in and click track
        if (self._click):
            pass



        # pass 5: Apply dynamics for each instrument or instrument groups

        # pass 6: Merge all wave files into one



    def play(self, score):
        pass


