import unittest
import hashlib
import mmap


from besampler.wavefile import WaveFile
from .utils import sha256sum


class TestWavefile(unittest.TestCase):
    def test_delay(self):
        snd = WaveFile.from_file("samples/whistle.wav")
        snd.delay(1000)
        snd.export("test_delay.wav")
        # Jsut check, that the expected file has been generated. 
        # You need to listen to the file and check, if the result is ok.
        self.assertEqual("4cd6803024d3a284", sha256sum("test_delay.wav")[0:16])

    def test_pan(self):
        snd = WaveFile.from_file("samples/whistle.wav").to_stereo()
        snd.pan(-1.0)
        snd.export("test_pan_left.wav")
        
        snd = WaveFile.from_file("samples/whistle.wav").to_stereo()
        snd.pan(1.0)
        snd.export("test_pan_right.wav")
        # Jsut check, that the expected file has been generated. 
        # You need to listen to the file and check, if the result is ok.
        self.assertEqual("4950314bff1ba471", sha256sum("test_pan_left.wav")[0:16])
        self.assertEqual("1c6b0c69d5481510", sha256sum("test_pan_right.wav")[0:16])
