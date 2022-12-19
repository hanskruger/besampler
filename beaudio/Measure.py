from collections import namedtuple
from functools import reduce
import numpy as np
import datetime
import re, os
import wave
from pydub import AudioSegment
from pathlib import Path

def ms(value):
    return datetime.timedelta(milliseconds=int(value))


class WaveFile(object):
    def __init__(self, hz, length_ms, channels = 1):
        pass

    @staticmethod
    def from_file(filename):
        audio_data = AudioSegment.from_file(filename)
        ret = WaveFile(len(audio_data), audio_data.frame_rate)
        ret._audio_data = audio_data
        return ret

    @staticmethod
    def silence(length_ms, hz):
        ret = WaveFile(length_ms, hz)
        ret._audio_data = AudioSegment.silent(duration = length_ms, frame_rate = hz)
        return ret

    def export(self, name):
        self._audio_data.export(name, format="wav")

    def overlay(self, other, offset):
        new_data = self._audio_data.overlay(other._audio_data, position=offset)
        self._audio_data = new_data
        return self

    @staticmethod
    def empty(hz, duration_ms):
        cnt = int(hz * duration_ms / 1000)
        return Wavefile(hz, np.zeros(cnt))
        pass




class Clock():
    def __init__(self, hz, offset_ms = 0):
        self._hz = hz
        self._offset = float(offset) # number of samples.

    def __add__(self, b):
        if isinstance(b, Clock):
            if b._hz == self._hz:
                return Clock(self._hz, self._offset + b._offset)
            b = b.to_ms()
        if isinstance(b, datetime.timedelta):
            return Clock(self._hz, self._offset + b.total_seconds() * self._hz)
        if isinstance(b, int) or isinstance(b, float):
            return Clock(self._hz, self._offset + b)
        raise RuntimeError(f"Unsupported type {b.__class__}.")

    def to_ms(self):
        return datetime.timedelta(milliseconds= int(self._offset/self._hz))

    def index(self):
        return int(0)

class TimeSignature():
    def __init__(self, pulses = 4, note_value = 4):
        self._pulses = 4
        self._note_value = 4

    @property
    def pulses(self):
        return self._pulses

    @property
    def note_value(self):
        return self._note_value

class Sample():
    def __init__(self, file_name, offset_ms = 0, bpm = 100):
        self._sample_rate           = 0
        self._number_samples        = 0
        self._offset_ms = offset_ms = 0
        self._wave = WaveFile.from_file(file_name)

        # check correct frame rate etc.


        with wave.open(file_name,"rb") as f:
            self._sample_rate    = f.getframerate()
            self._number_samples = f.getnframes()
        pass

    @property
    def file_name(self):
        return self._file_name

    @property
    def length_ms(self):
        return 1000.0 * self._number_samples / self._sample_rate

    @property
    def offset_ms(self):
        return self._offset_ms

    @property
    def wave(self):
        return self._wave


class Pattern():
    def __init__(self, pattern):
        self._pattern = pattern
        self._beats   = re.split("\s+", self._pattern)
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

class Instrument():
    pass
    def __init__(self, name, bpm = 120):
        self._name = name
        self._patterns = {}
        self._bpm = bpm
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

    def __str__(self):
        return self._name
    def __repr__(self):
        return f"<Instrument {self._name} at 0x{id(self):x}>"


class Measure():
    def __init__(self, notes, time_signature = TimeSignature()):
        self._time_signature = time_signature
        self._notes = notes
        pass

    def parse(inp, time_signature = TimeSignature(), strict = True):
        '''
        If strict is true, parsing will fail, if wrong number of beats are given.
        '''
        inp_orig = inp
        inp = inp.strip("\t ")
        inp = re.split("\s+", inp)

        if strict and len(inp) != time_signature.pulses:
            raise RuntimeError("Number of pulses in measure must be exactly {time_signature.pulses}.")

        return Measure(inp, time_signature)

    @property
    def notes(self):
        return self._notes

    def parse_line(inp):
        '''
        Parse a whole line, with prefix and trailing text and mutiple bars sepparated by |
        '''
        return [ Measure.parse(inp)  ]

    def __str__(self):
        return " ".join(self._notes)

    def __repr__(self):
        return f"<Instrument {self} at 0x{id(self):x}>"


class Score():
    def __init__(self, time_signature = TimeSignature()):
        self._score = []
        self._time_signature = time_signature

    @property
    def time_signature(self):
        return self._time_signature

    def add_staff(self, staff):
        return staff

    def add_measure(self, *instruments):
        self._score.append(instruments)
        pass

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
            for e in m:
                if e.staff == staff:
                    yield e

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

def estacio_caixa():
    cax = Instrument("caixa", bpm = 100)
    cax.add_pattern("XxLx X.X. x...").add_samples(
            Sample("../samples/estácio/caixa_1/100bpm/virada1-1.wav"),
            Sample("../samples/estácio/caixa_1/100bpm/virada1-2.wav"))
    cax.add_pattern("/ / / /").add_samples(
            Sample("../samples/estácio/caixa_1/100bpm/groove-1.wav"),
            Sample("../samples/estácio/caixa_1/100bpm/groove-2.wav"))

#    cax.add_pattern("/ / / R...").add_samples(bpm = 100, "caixa_groove_1_100bpm.wav", "caixa_groove_2_100bpm.wav")
#    cax.add_pattern("/ / R...").add_samples().bpm(100).wav("caixa_groove_1_100bpm.wav", "caixa_groove_2_100bpm.wav")
#    cax.add_pattern("/ R...").add_samples().bpm(100).wav("caixa_groove_1_100bpm.wav", "caixa_groove_2_100bpm.wav")
#    cax.add_pattern("R...").add_samples().bpm(100).wav("caixa_groove_1_100bpm.wav", "caixa_groove_2_100bpm.wav")
    return cax

def bossa():
    sc = Score();
    tam = sc.add_staff(Staff("Tamborim"))
    cho = sc.add_staff(Staff("Chocalho"))
    rep = sc.add_staff(Staff("Repinique"))
    cax = sc.add_staff(Staff("Caixa"))
    pri = sc.add_staff(Staff("Primeira"))
    seg = sc.add_staff(Staff("Segunda"))
    ter = sc.add_staff(Staff("Terceira"))

    m = sc.add_measure(
        cho("xxxx x.x. x... ...."),
        tam("xxxx x.x. x... ...."),
        cax("XxLx X.X. x... ...."),
        pri(".... ..R. .... ..R."),
        seg("R... .... R... ...."),
        ter(".... ..R. .... ..R.")
    )

    # Add a Bar of Groove
    m = sc.add_measure(
        cho("- - - -"),
        tam("- - - -"), # muted!
        cax("/ / / /"),
        pri("/ / / /"),
        seg("/ / / /"),
        ter("/ / / /")
    )
    m = sc.add_measure(
        cho("-    -   -    -   "),
        tam("xxx  xxx xxx  xxx "), # triolen
        cax("/    /   /    /   "),
        pri("/    /   /    /   "),
        seg("/    /   /    /   "),
        ter("/    /   /    /   ")
    )

    m = sc.add_measure(
        cho("-    - - -"),
        tam("x... - - -"),
        cax("/    / / /"),
        pri("/    / / /"),
        seg("/    / / /"),
        ter("/    / / /")
    )

    # Groove
    m = sc.add_measure(
        cho("/ / / /"),
        tam("/ / / /"),
        cax("/ / / /"),
        pri("/ / / /"),
        seg("/ / / /"),
        ter("/ / / /")
    )
    m = sc.add_measure(
        cho("xxxx x.x. x... ...."),
        tam("xxxx x.x. x... ...."),
        cax("XxLx X.X. x... ...."),
        pri(".... ..R. .... ..R."),
        seg("R... .... R... ...."),
        ter(".... ..R. .... ..R.")
    )

    return sc

if __name__ == "__main__":
    player = Player(bpm = 100)

    player.add_artist("cax1", staff="Caixa", instrument=estacio_caixa())

    score = bossa()
    player.synthesize(score)
