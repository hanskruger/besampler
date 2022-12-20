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
