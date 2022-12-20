from collections import namedtuple
from functools import reduce
import numpy as np
import datetime
import re, os, sys
import wave
import argparse
import traceback
import logging
from pydub import AudioSegment
from pathlib import Path
from functools import total_ordering

from besampler import *
from besampler.sample import Sample
from besampler.sample_builder import SampleBuilder

parser = argparse.ArgumentParser(
                    prog = 'Bloco Esperança Sampler',
                    description = 'Sample Samba Breaks using short samples.')
parser.add_argument('score', type=Path, help="The score to be sampled")           # positional argument
parser.add_argument('-v', '--verbose', action='store_true')  # on/off flag
parser.add_argument('-D', '--debug', action='store_true')  # on/off flag

def click():
    ins = Instrument("Click", bpm = 100)
    ins.add_pattern("X...").add_samples(
            Sample("samples/click-hard.wav"))
    ins.add_pattern("x...").add_samples(
            Sample("samples/click-soft.wav"))
    return ins

def apito():
    ins = Instrument("Apito", bpm = 100)
    ins.add_pattern("x").add_samples(
            Sample("samples/whistle.wav"))
    return ins

def estacio_caixa():
    cax = Instrument("caixa", bpm = 100)
    cax.add_pattern("|XxLx X.X. X...").add_samples(
            Sample("samples/estácio/caixa_1/100bpm/virada1-1.wav"),
            Sample("samples/estácio/caixa_1/100bpm/virada1-2.wav"))
    cax.add_pattern("|/ / / /").add_samples(
            Sample("samples/estácio/caixa_1/100bpm/groove-1.wav"),
            Sample("samples/estácio/caixa_1/100bpm/groove-2.wav"))
    
    cax.add_pattern("x...").add_samples(
            Sample("samples/estácio/caixa_1/100bpm/R___-1.wav"))
    
    cax.add_pattern("x.x.").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/caixa_1/100bpm/R___-1.wav"))
                .add_subsample(Sample("samples/estácio/caixa_1/100bpm/R___-1.wav"), ".x")
                .build()
                )
    cax.add_pattern("x.x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/caixa_1/100bpm/R___-1.wav"))
                .add_subsample(Sample("samples/estácio/caixa_1/100bpm/R___-1.wav"), "..x")
                .build()
                )
    cax.add_pattern("xxx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/caixa_1/100bpm/R___-1.wav"))
                .add_subsample(Sample("samples/estácio/caixa_1/100bpm/R___-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/caixa_1/100bpm/R___-1.wav"), "..x")
                .build()
                )

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
        cax("XxLx X.X. X... ...."),
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
        cax("XxLx X.X. X... ...."),
        pri(".... ..R. .... ..R."),
        seg("R... .... R... ...."),
        ter(".... ..R. .... ..R.")
    )

    return sc


def main(args):
   
    if (not args.score or not args.score.exists()):
        raise RuntimeError(f"File {args.score} does not exist")

    player = Player(bpm = 100)

    player.add_artist("cax1", staff="Caixa", instrument=estacio_caixa())
    player.add_artist("click", staff="Click", instrument=click())
    player.add_artist("apito", staff="Apito", instrument=apito())

    score = Score.from_file(args.score)
    #score = bossa()
    player.synthesize(score)


if __name__ == "__main__":
    _LOG_FMT="%(levelname)s: %(message)s"
    args = parser.parse_args()
    try:
        if (args.debug):
            logging.basicConfig(format=_LOG_FMT, level=logging.DEBUG)
        elif(args.verbose):
            logging.basicConfig(format=_LOG_FMT, level=logging.INFO)
        else:
            logging.basicConfig(format=_LOG_FMT, level=logging.WARN)
        main(args)
    except Exception as e:
        if (args.debug):
            traceback.print_exc()
        sys.exit(f"Error: {e}") 
    sys.exit() 
