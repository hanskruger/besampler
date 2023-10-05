import tempfile

from .wavefile import WaveFile
from .sample   import Sample
from .utils   import Clock
from .player import ProgEntry
from .pattern import match_pause

class SampleBuilder(object):
    def __init__(self, bpm, frame_rate):
        self._bpm = bpm
        self._frame_rate = frame_rate
        self._build_instructions = []

    def add_subsample(self, sample, shift = None, gain = None, pulse = 0):
        # TODO: Check for correct frame rate of samples!
        self._build_instructions.append( (sample, shift, gain, pulse))
        return self

    def build(self):
        #max_offset = max( map( lambda x: x[0].offset_ms, self._build_instructions))
        #max_length = max( map( lambda x: x[0].length_ms - x[0].offset_ms, self._build_instructions))
        max_offset, max_length = (0,0)
        clk = Clock(self._bpm, frame_rate=self._frame_rate, offset_ms = 0)

        # pass 0: get boundries 
        for sample, shift, gain, pulse in self._build_instructions:
            offset = clk.pulse( pulse, shift ) - sample.offset_ms
            max_offset = min(max_offset, offset)
            max_length = max(max_length, offset + sample.length_ms)

        clk = Clock(self._bpm, frame_rate=self._frame_rate, offset_ms = abs(max_offset))

        wav = WaveFile.silence(max_length + abs(max_offset) + clk.pulse_length_ms, self._frame_rate)

        for sample, shift, gain, pulse in self._build_instructions:
            offset = clk.pulse( pulse, shift ) - sample.offset_ms
            #print(offset, p.pattern.sample(p.repeat_index).wave)
            if gain:
                wav.overlay(sample.wave.clone().gain(gain), offset=offset)
            else:
                wav.overlay(sample.wave , offset=offset)

        return Sample(wav, offset_ms = max_offset)
    
    def apply(self, pattern, idx, programm, score, staff, staffline, artist, repeat_index):
        programm.append( ProgEntry( self.sample(repeat_index), repeat_index, idx, pattern) )
        return len(pattern)



