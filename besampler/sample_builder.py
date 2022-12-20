import tempfile

from .wavefile import WaveFile
from .sample   import Sample
from .utils   import Clock

class SampleBuilder(object):
    def __init__(self, bpm, frame_rate):
        self._bpm = bpm
        self._frame_rate = frame_rate
        self._build_instructions = []

    def add_subsample(self, sample, shift = None):
        # TODO: Check for correct frame rate of samples!
        self._build_instructions.append( (sample, shift))
        return self

    def build(self):
        max_offset = max( map( lambda x: x[0].offset_ms, self._build_instructions))
        max_length = max( map( lambda x: x[0].length_ms - x[0].offset_ms, self._build_instructions))
        
        clk = Clock(self._bpm, frame_rate=self._frame_rate, offset_ms = max_offset)
        
        wav = WaveFile.silence(max_length + max_offset, self._frame_rate)
        
        for sample, shift in self._build_instructions:
            offset = clk.pulse( 0, shift ) - sample.offset_ms
            #print(offset, p.pattern.sample(p.repeat_index).wave)
            wav.overlay(sample.wave , offset=offset)

        return Sample(wav, offset_ms = max_offset)
