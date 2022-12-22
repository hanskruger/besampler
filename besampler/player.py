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
from .pattern  import match_pause, match_repeat, parse_tone
from .utils    import Clock

Prog      = namedtuple("Prog",["programm", ])
ProgEntry = namedtuple("ProgEntry",["sample", "repeat_index", "staff_index"])

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
        self._track_cb = lambda snd,artist,score : True

    @property
    def bpm(self):
        return self._bpm

    def add_track_callback(self, cb):
        '''
        Provide a callback that will be called once an inidvidual mono track has been creted for a given artist. 
        Allows calling applicaitonn to store individual tracks.

        The callback must accept 3 argument: the sound-file, the artist and the score
        '''
        self._track_cb = cb

    def __synth_measure(self, m):
        pass

    @property
    def instruments(self):
        instruments = []
        for staff in self._artist.values():
            instruments.extend( map(lambda x: x.instrument, staff))
        return list(set(instruments))
    
    @property
    def artists(self):
        ret = []
        for staff in self._artist.values():
            ret.extend( map(lambda x: x.name, staff))
        return list(set(ret))

    def add_artist(self, name, staff, instrument, settings = None):
        settings = InstrumentSettings() if not settings else settings
        Artist = namedtuple("Artist",["name", "staff","settings", "instrument"])
        # artists are added grouped by the staff they play!
        self._artist.setdefault(staff, []).append(Artist(name, staff, settings, instrument))
        return settings

    def _compile_artist(self, artist, staff, score):
        logging.info(f"Generating audio track for artist {artist.name}({artist.instrument.name}), staff {staff}.")
        head_index = 0;
        ONE_BAR_PAUSE = score.time_signature.fill_bar("-") 
        instrument = artist.instrument
        measures = list(score.measures(staff))
        #print(staff, measures)
        staff_line = list(map(parse_tone, reduce(lambda a,b: a+b,  map(lambda x: x.measure.notes if x else ONE_BAR_PAUSE, measures))))
        prog = []
        last_pattern = None

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
            repeat_index = 0 if (not prog or last_pattern != pat) else prog[-1].repeat_index + 1
            last_pattern = pat
            consumed = pat.apply(idx, prog, score, staff, staff_line, artist, repeat_index  )
            idx = idx + consumed

        # start synthesizing the sound file.

        return Prog(prog)

    def _synth_artist(self, prog, artis, score):
        clk = Clock(self._bpm, frame_rate=self._freq, offset_ms=0)

        lenght_ms      = 60000.0 * score.length * score.time_signature.pulses / self._bpm
        lenght_samples = lenght_ms * self._freq / 1000.0
        instrument = artis.instrument

        wav = WaveFile.silence(lenght_ms, self._freq)

        for p in prog.programm:
            offset =  clk.pulse( p.staff_index )
            #print(offset, p.pattern.sample(p.repeat_index).wave)
            wav.overlay(p.sample.wave , offset=offset)

        return wav

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
        out = None

        # pass 2: Check for instrumetns for all staff lines
        for s in staffs:
            if s.name not in self._artist.keys():
                logging.warning(f"No artist given for staff {s}.")
                continue
            for i in self._artist[s.name]:
                # pass 3: For each staff line and isntrument, generate the wave file
                prog = self._compile_artist(i, s, score)
                snd = self._synth_artist(prog, i, score)
                self._track_cb(snd, i, score)
                #print(prog.programm)

                # pass 4: Apply PAN, gain, deplay etc. for each instrument
                snd.delay(i.settings.delay_ms) \
                    .gain(i.settings.gain)     \
                    .to_stereo(i.settings.pan)
                # pass 5: Apply dynamics for each instrument or instrument groups

                # pass 6: Merge all wave files into one
                out = snd if None is out else out.overlay(snd, 0)

        return out



    def play(self, score):
        pass


