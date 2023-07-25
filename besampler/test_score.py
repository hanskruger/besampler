import unittest

from besampler import Score


class TestScore(unittest.TestCase):
    def test_parse_bossa(self):
        Score.from_file("examples/bossa.txt")

    def test_match_latex(self):
        s = Score().match_latex("Tamborim &/   &/   &/   &/   &x...&....&....&....&xxx &xxx &xxx &xxx &x...&....&....&....\\\\ \\hline % blah balh balh")
        self.assertIsNotNone(s)
        self.assertEqual(s.instrument, "Tamborim")
        self.assertEqual(s.staff_line, "Tamborim |/    /    /    /   |x... .... .... ....|xxx  xxx  xxx  xxx |x... .... .... ....|")

