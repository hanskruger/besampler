import unittest

from besampler import Score


class TestScore(unittest.TestCase):

    def test_parse_bossa(self):
        Score.from_file("examples/bossa.txt")
