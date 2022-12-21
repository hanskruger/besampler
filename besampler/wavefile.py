from collections import namedtuple
from functools import reduce
import numpy as np
import datetime
import re, os
import wave
from pydub import AudioSegment
from pathlib import Path
from functools import total_ordering

class WaveFile(object):
    def __init__(self, frame_rate, length_ms, channels = 1):
        self._frame_rate = frame_rate
        self._audio_data = None
        pass

    @staticmethod
    def from_file(filename):
        audio_data = AudioSegment.from_file(filename)
        ret = WaveFile(audio_data.frame_rate, len(audio_data))
        ret._audio_data = audio_data
        return ret

    
    def export(self, filename):
        return self._audio_data.export(filename)

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

    @property
    def frame_rate(self):
        return self._frame_rate
    
    @property
    def number_of_samples(self):
        return self._frame_rate * len(self._audio_data)

    def delay(self, ms):
        if (0 == ms):
            return self
        if (not self._audio_data):
            raise RuntimeError("Nothing to delay")
        if (ms < 0):
            raise RuntimeError("Dealy must be a positive number")


        new_data =  AudioSegment.silent(duration = ms, frame_rate = self._audio_data.frame_rate) + self._audio_data
        self._audio_data = new_data
        return self

    def to_stereo(self, pan = 0.0):
        stereo_sound = AudioSegment.from_mono_audiosegments(self._audio_data, self._audio_data)
        if (0 != pan):
            stereo_sound = stereo_sound.pan(pan)
        self._audio_data = stereo_sound
        return self

    def gain(self, db):
        self._audio_data = self._audio_data.apply_gain(db) 
        return self

    def pan(self, pan = 0.0):
        self._audio_data = self._audio_data.pan(pan) 
        return self



