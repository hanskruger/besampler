from collections import namedtuple
from functools import reduce
import numpy as np
import datetime
import re, os
import wave
from pydub import AudioSegment
from pathlib import Path
from functools import total_ordering

from besampler import *
from besampler.sample import Sample



def estacio_caixa():
    cax = Instrument("caixa", bpm = 100)
    cax.add_pattern("XxLx X.X. x...").add_samples(
            Sample("samples/estácio/caixa_1/100bpm/virada1-1.wav"),
            Sample("samples/estácio/caixa_1/100bpm/virada1-2.wav"))
    cax.add_pattern("/ / / /").add_samples(
            Sample("samples/estácio/caixa_1/100bpm/groove-1.wav"),
            Sample("samples/estácio/caixa_1/100bpm/groove-2.wav"))

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

    score = Score.from_file("examples/bossa.txt")
    score = bossa()
    player.synthesize(score)

