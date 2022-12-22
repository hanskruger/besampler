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
from pydub.playback import play

from pathlib import Path
from functools import total_ordering

from besampler import *
from besampler.sample import Sample
from besampler.sample_builder import SampleBuilder

parser = argparse.ArgumentParser(
                    prog = 'Bloco Esperança Sampler',
                    description = 'Sample Samba Breaks using short samples.')
parser.add_argument('score', type=Path, help="The score to be sampled")           # positional argument
parser.add_argument('-o', '--out',   type=Path, help="name of the output file")           # positional argument
parser.add_argument('-v', '--verbose', action='store_true')  # on/off flag
parser.add_argument('-D', '--debug', action='store_true')  # on/off flag
parser.add_argument('--count_in', action='store_true')  # on/off flag
parser.add_argument('--click', action='store_true')  # on/off flag
parser.add_argument('--info', action='store_true', help="print score info and exit")
parser.add_argument('--tracks', action='store_true')
parser.add_argument('--bpm', default=100, type=int, help="The output speed")
parser.add_argument('-f', '--format', default="mp3", help='format of output (wav|mp3)')  # on/off flag

def click():
    ins = Instrument("Click", bpm = 100)
    ins.add_pattern("X").add_samples(
            Sample("samples/click-hard.wav"))
    ins.add_pattern("x").add_samples(
            Sample("samples/click-soft.wav"))
    return ins

def voz():
    ins = Instrument("Click", bpm = 100)
    ins.add_pattern("ES..").add_samples(
            Sample("samples/voz-es.wav"))
    ins.add_pattern("PE..").add_samples(
            Sample("samples/voz-pe.wav"))
    ins.add_pattern("RAN.").add_samples(
            Sample("samples/voz-ran.wav"))
    ins.add_pattern("CA..").add_samples(
            Sample("samples/voz-ca.wav"))
    ins.add_pattern("ESPE").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/voz-es.wav"))
                .add_subsample(Sample("samples/voz-pe.wav"), ".x")
                .build()
                )
    return ins

def apito():
    ins = Instrument("Apito", bpm = 100)
    ins.add_pattern("x").add_samples(
            Sample("samples/whistle.wav"))
    ins.add_pattern("x.x.").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/whistle.wav"))
                .add_subsample(Sample("samples/whistle.wav"), ".x")
                .build()
                )
    return ins

def repi():
    cax = Instrument("Repi", bpm = 100)
    cax.add_pattern("cccc cccc").add_samples(
            Sample("samples/estácio/100bpm/repi-chamada-1.wav"))
    cax.add_pattern("x").add_samples(
            Sample("samples/estácio/100bpm/repi-x-1.wav"))
    cax.add_pattern("xxxx").alias("/").add_samples(
            Sample("samples/estácio/100bpm/repi-xxxx-1.wav"),
            Sample("samples/estácio/100bpm/repi-xxxx-2.wav"))
    cax.add_pattern("x.x.").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/repi-x-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/repi-x-1.wav"), ".x")
                .build()
                )
    cax.add_pattern("x..x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/repi-x-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/repi-x-1.wav"), "...x")
                .build()
                )
    cax.add_pattern("..x.").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/repi-x-1.wav"), ".x")
                .build()
                )
    cax.add_pattern(".x..").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/repi-x-1.wav"), ".x..")
                .build()
                )
    cax.add_pattern("x.x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/repi-x-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/repi-x-1.wav"), "..x")
                .build()
                )
    cax.add_pattern("xxx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/repi-x-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/repi-x-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/100bpm/repi-x-1.wav"), "..x")
                .build()
                )
    return cax

def estacio_caixa():
    cax = Instrument("caixa", bpm = 100)
    cax.add_pattern("|XxLx").add_samples(
            Sample("samples/estácio/100bpm/caixa-xxlx-1.wav"),
            Sample("samples/estácio/100bpm/caixa-xxlx-2.wav"))
    cax.add_pattern("|/ / / /") \
            .add_samples(
                Sample("samples/estácio/100bpm/caixa-groove-1.wav")
                )

    cax.add_pattern("/").alias("xxxx").add_samples(
            Sample("samples/estácio/100bpm/caixa-xxxx-1.wav"),
            Sample("samples/estácio/100bpm/caixa-xxxx-2.wav"),
            Sample("samples/estácio/100bpm/caixa-xxxx-3.wav"))

    cax.add_pattern("x...").add_samples(
            Sample("samples/estácio/100bpm/caixa-x___-1.wav"))

    cax.add_pattern("x.x.").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"), ".x")
                .build()
                )
    cax.add_pattern("x..x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"), "...x")
                .build()
                )
    cax.add_pattern("..x.").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"), ".x")
                .build()
                )
    cax.add_pattern(".x..").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"), ".x..")
                .build()
                )
    cax.add_pattern("x.x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"), "..x")
                .build()
                )
    cax.add_pattern(".xx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"), "..x")
                .build()
                )
    cax.add_pattern("xxx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"), "..x")
                .build()
                )

#    cax.add_pattern("/ / / R...").add_samples(bpm = 100, "caixa_groove_1_100bpm.wav", "caixa_groove_2_100bpm.wav")
#    cax.add_pattern("/ / R...").add_samples().bpm(100).wav("caixa_groove_1_100bpm.wav", "caixa_groove_2_100bpm.wav")
#    cax.add_pattern("/ R...").add_samples().bpm(100).wav("caixa_groove_1_100bpm.wav", "caixa_groove_2_100bpm.wav")
#    cax.add_pattern("R...").add_samples().bpm(100).wav("caixa_groove_1_100bpm.wav", "caixa_groove_2_100bpm.wav")
    return cax

def primeira():
    ins = Instrument("Primeira", bpm = 100)
    ins.add_pattern("1...").alias("x", "x...").add_samples(
            Sample("samples/estácio/100bpm/surdo_1a-1.wav"),
            Sample("samples/estácio/100bpm/surdo_1a-2.wav"))
    ins.add_pattern("1.1.").alias("x.x.", "xx"). add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"), ".x")
                .build()
                )
    ins.add_pattern("1..1").alias("x..x"). add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"), "...x")
                .build()
                )
    ins.add_pattern("..1.").alias("..x.").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"), ".x")
                .build()
                )
    ins.add_pattern(".1..").alias(".x..").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"), ".x..")
                .build()
                )
    ins.add_pattern("1.1").alias("x.x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"), "..x")
                .build()
                )
    ins.add_pattern("xxx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"), "..x")
                .build()
                )
    ins.add_pattern(".xx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/100bpm/surdo_1a-1.wav"), "..x")
                .build()
                )
    return ins

def terceira():
    ins = Instrument("Terceira", bpm = 100)
    ins.add_pattern("3...").alias("3", "x", "x...").add_samples(
            Sample("samples/estácio/100bpm/surdo_3a-1.wav"),
            Sample("samples/estácio/100bpm/surdo_3a-2.wav"))
    ins.add_pattern("3.3.").alias("33", "xx", "x.x.").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"), ".x")
                .build()
                )
    ins.add_pattern("3..3").alias("x..x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"), "...x")
                .build()
                )
    ins.add_pattern("..3.").alias("..x.").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"), ".x")
                .build()
                )
    ins.add_pattern(".3..").alias(".x..").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"), ".x..")
                .build()
                )
    ins.add_pattern("3.3").alias("x.x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"), "..x")
                .build()
                )
    ins.add_pattern("33.3").alias("xx.x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"), ".x..")
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"), "...x")
                .build()
                )
    ins.add_pattern("xxx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"), "..x")
                .build()
                )
    ins.add_pattern(".xx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/100bpm/surdo_3a-1.wav"), "..x")
                .build()
                )
    return ins


def segunda():
    ins = Instrument("Segunda", bpm = 100)
    ins.add_pattern("2...").alias("x...", "x").add_samples(
            Sample("samples/estácio/100bpm/surdo_2a-1.wav"), 
            Sample("samples/estácio/100bpm/surdo_2a-2.wav"))
    ins.add_pattern("2.2.").alias("x.x.", "22", "xx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"), ".x")
                .build()
                )
    ins.add_pattern("2..2").alias("x..x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"), "...x")
                .build()
                )
    ins.add_pattern("..2.").alias("..x.").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"), ".x")
                .build()
                )
    ins.add_pattern(".2..").alias(".x..").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"), ".x..")
                .build()
                )
    ins.add_pattern("2.2").alias("x.x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"), "..x")
                .build()
                )
    ins.add_pattern("xxx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"), "..x")
                .build()
                )
    ins.add_pattern(".xx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/100bpm/surdo_2a-1.wav"), "..x")
                .build()
                )
    return ins


def tamborim():
    ins = Instrument("Tamborim", bpm = 100)
    ins.add_pattern("x").alias("x", "x..", "x...", "x.").add_samples(
            Sample("samples/estácio/100bpm/tamborim-x-1.wav"))
    ins.add_pattern("|xxx xxx xxx xxx x... .... .... ....").add_samples(
            Sample("samples/estácio/100bpm/tamborim-subida-1.wav"),
            Sample("samples/estácio/100bpm/tamborim-subida-2.wav"))
    ins.add_pattern("xxxx").alias("/").add_samples(
            Sample("samples/estácio/100bpm/tamborim-single_groove-1.wav"),
            Sample("samples/estácio/100bpm/tamborim-single_groove-2.wav"))
    ins.add_pattern("xxx").add_samples(
            Sample("samples/estácio/100bpm/tamborim-xxx-1.wav"),
            Sample("samples/estácio/100bpm/tamborim-xxx-2.wav"),
            Sample("samples/estácio/100bpm/tamborim-xxx-3.wav"))
    ins.add_pattern("x.x.").alias("xx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/tamborim-x-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/tamborim-x-1.wav"), ".x")
                .build()
                )
    ins.add_pattern("..x.").alias("xx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/tamborim-x-1.wav"), ".x")
                .build()
                )
    ins.add_pattern(".x..").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/tamborim-x-1.wav"), ".x..")
                .build()
                )
    ins.add_pattern("x..x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/tamborim-x-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/tamborim-x-1.wav"), "...x")
                .build()
                )
    ins.add_pattern("x.x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/tamborim-x-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/tamborim-x-1.wav"), "..x")
                .build()
                )
    ins.add_pattern(".xx").alias("xx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/tamborim-x-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/100bpm/tamborim-x-1.wav"), "..x")
                .build()
                )
    return ins

def chocalho():
    ins = Instrument("Chocalho", bpm = 100)
    ins.add_pattern("|/ / / /").alias("/xxxx xxxx xxxx xxxx").add_samples(
            Sample("samples/estácio/100bpm/chocalho-groove-1.wav"),
            Sample("samples/estácio/100bpm/chocalho-groove-2.wav"))
    ins.add_pattern("x").alias("x", "x..", "x...", "x.").add_samples(
            Sample("samples/estácio/100bpm/chocalho-x-1.wav"))
    ins.add_pattern("xxxx").alias("/").add_samples(
            Sample("samples/estácio/100bpm/chocalho-xxxx-1.wav"),
            Sample("samples/estácio/100bpm/chocalho-xxxx-2.wav"),
            Sample("samples/estácio/100bpm/chocalho-xxxx-3.wav"))
    ins.add_pattern("x.x.").alias("xx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"), ".x")
                .build()
                )
    ins.add_pattern("x..x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"), "...x")
                .build()
                )
    ins.add_pattern("..x.").alias(".x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"), ".x")
                .build()
                )
    ins.add_pattern(".x..").alias(".x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"), ".x..")
                .build()
                )
    ins.add_pattern("xxx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"), "..x")
                .build()
                )
    ins.add_pattern(".xx").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"), ".x.")
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"), "..x")
                .build()
                )
    ins.add_pattern("x.x").add_samples(
            SampleBuilder(100, 48000)
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"))
                .add_subsample(Sample("samples/estácio/100bpm/chocalho-x-1.wav"), "..x")
                .build()
                )
    return ins

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

def print_info(args, score, player):
    MSG= f"""# Info about score and player
score.filename:       {args.score}
score.time.signature: {score.time_signature.pulses}/{score.time_signature.note_value}
score.staffs:         {", ".join(map(str, score.staffs))}
player.bpm:           {player.bpm}
player.instruments:   {", ".join(map(str, player.instruments))}
player.artists:       {", ".join(map(str, player.artists))}
"""
    print(MSG)

def main(args):

    if (not args.score or not args.score.exists()):
        raise RuntimeError(f"File {args.score} does not exist")

    def write_track_cb(snd, artist, score):
        filename = Path( f"{artist.instrument.name}_{artist.name}.wav")
        logging.info(f"Writing track for artist {artist.instrument.name}/{artist.name} to {filename}.")
        snd.export(filename, format="wav")

    player = Player(bpm = 100)

    player.add_artist("cho1",     staff="Chocalho", instrument=chocalho()).set_pan(0.2).set_gain(-6)
    player.add_artist("tam1",     staff="Tamborim", instrument=tamborim()).set_pan(0.3)
    player.add_artist("rep1",     staff="Repi",     instrument=repi())
    player.add_artist("cax1",     staff="Caixa",    instrument=estacio_caixa()).set_pan(-0.1).set_gain(1.0)
    player.add_artist("1a",       staff="Primeira", instrument=primeira()).set_pan(0.6).set_gain(-6)
    player.add_artist("2a",       staff="Segunda",  instrument=segunda()).set_pan(-0.6).set_gain(-6)
    player.add_artist("3a",       staff="Terceira", instrument=terceira()).set_gain(-6)
    player.add_artist("voz",      staff="Voz",      instrument=voz())
    player.add_artist("apito",    staff="Apito",    instrument=apito())
    player.add_artist("click",    staff="Click",    instrument=click())
    player.add_artist("count_in", staff="Count In", instrument=apito())


    if (args.tracks):
        player.add_track_callback(write_track_cb)

    score = Score.from_file(args.score)

    if (args.info):
        print_info(args, score, player)
        sys.exit()


    if(args.count_in):
        score.add_count_in()
    if(args.click):
        score.add_click()
    #score = bossa()
    snd = player.synthesize(score)

    snd.speedup( args.bpm / player.bpm)
    #x = snd._audio_data.speedup(1.35, 150, 25)
    #x.export(args.out, format="wav")
    if (args.out):
        snd.export(args.out, format=args.format)
    else:
        play(snd._audio_data)

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
