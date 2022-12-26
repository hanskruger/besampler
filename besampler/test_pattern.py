from tempfile import NamedTemporaryFile
import unittest

from besampler import Score
from besampler.pattern import *

class TestPattern(unittest.TestCase):
    def test_parse_bossa(self):
        self.assertEqual(["", "s", "s", "s"], parse_pattern("|.... s s s |").pattern)

    def test_parse_tone(self):
        self.assertEqual("x", parse_tone("x..."))
        self.assertEqual("x.x.", parse_tone("x.x."))
        self.assertEqual("x.x", parse_tone("x.x"))
        self.assertEqual("..x.", parse_tone("..x."))
