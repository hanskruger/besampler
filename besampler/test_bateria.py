from tempfile import NamedTemporaryFile
import unittest
import yaml

from besampler import Score
from besampler.pattern import *
from besampler.bateria import Bateria

class TestBateria(unittest.TestCase):
    def test_parse_bossa(self):
        self.assertEqual(["", "s", "s", "s"], parse_pattern("|.... s s s |").pattern)


    def test_parse_estacio(self):
        bat = Bateria.from_file("samples/manifest.yaml")
