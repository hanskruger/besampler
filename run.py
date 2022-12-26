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
from besampler.bateria import Bateria

parser = argparse.ArgumentParser(
                    prog = 'Bloco Esperança Sampler',
                    description = 'Sample Samba Breaks using short samples.')
parser.add_argument('bateria', type=Path, help="The path to bataria files.")           # positional argument
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

parser.add_argument('--mute', help='Mute the given aritsts.')  # on/off flag
#parser.add_argument('--mute_staff', help='Mute all artists of the given staff.')  # on/off flag
#parser.add_argument('--mute_instrument', help='Mute all artist of the given instruments.')  # on/off flag
parser.add_argument('--mute_level', default=-60.0, type=float, help='Amount in dB, by which artitsts should be muted.')  # on/off flag

parser.add_argument('--solo', help='Only play the artists listed.')  # on/off flag
#parser.add_argument('--solo_staff', help='Only play the artists playing a given staff.')  # on/off flag
#parser.add_argument('--solo_instrument', help='Only play the artists playinf the given instruments.')  # on/off flag

parser.add_argument('--loop', default=1, type = int, help='Number of times a given score should be played.')


def click():
    ins = Instrument("Click", bpm = 100)
    ins.add_pattern("X").add_samples(
            Sample("samples/click-hard.wav"))
    ins.add_pattern("x").add_samples(
            Sample("samples/click-soft.wav"))
    return ins

def print_info(args, score, player):
    MSG= f"""# Info about score and player
score.filename:       {args.score}
score.time.signature: {score.time_signature.pulses}/{score.time_signature.note_value}
score.staffs:         {", ".join(map(str, score.staffs))}
player.bpm:           {player.bpm}
player.instruments:   {", ".join(map(str, player.instruments))}
player.artists:       {", ".join(map(lambda x: x.name, player.artists))}
"""
    print(MSG)

def main(args):

    if (not args.score or not args.score.exists()):
        raise RuntimeError(f"File {args.score} does not exist")

    def write_track_cb(snd, artist, score):
        filename = Path( f"{artist.instrument.name}_{artist.name}.wav")
        logging.info(f"Writing track for artist {artist.instrument.name}/{artist.name} to {filename}.")
        snd.export(filename, format="wav")


    bateria = Bateria.from_file(args.bateria)

    player = Player(bpm = 100)
    
    player.add_artist("cho1",     staff="Chocalho", instrument=bateria.instrument("Chocalho")).set_pan(0.2).set_gain(-6)
    player.add_artist("tam1",     staff="Tamborim", instrument=bateria.instrument("Tamborim")).set_pan(0.3)
    player.add_artist("cax1",     staff="Caixa",    instrument=bateria.instrument("Caixa")).set_pan(-0.1).set_gain(1.0)
    player.add_artist("rep1",     staff="Repi",     instrument=bateria.instrument("Repi"))
    player.add_artist("1a",       staff="Primeira", instrument=bateria.instrument("Primeira")).set_pan(0.6).set_gain(-6)
    player.add_artist("2a",       staff="Segunda",  instrument=bateria.instrument("Segunda")).set_pan(-0.6).set_gain(-6)
    player.add_artist("3a",       staff="Terceira", instrument=bateria.instrument("Terceira")).set_gain(-6)
    player.add_artist("apito",    staff="Apito",    instrument=bateria.instrument("Apito"))
    player.add_artist("voz",      staff="Voz",      instrument=bateria.instrument("Voz"))
    player.add_artist("count_in", staff="Count In", instrument=bateria.instrument("Apito"))

    #player.add_artist("cho1",     staff="Chocalho", instrument=chocalho()).set_pan(0.2).set_gain(-6)
    #player.add_artist("tam1",     staff="Tamborim", instrument=tamborim()).set_pan(0.3)
    #player.add_artist("1a",       staff="Primeira", instrument=primeira()).set_pan(0.6).set_gain(-6)
    #player.add_artist("2a",       staff="Segunda",  instrument=segunda()).set_pan(-0.6).set_gain(-6)
    #player.add_artist("3a",       staff="Terceira", instrument=terceira()).set_gain(-6)
    #player.add_artist("voz",      staff="Voz",      instrument=voz()).set_gain(-10)
    player.add_artist("click",    staff="Click",    instrument=click())


    muted_artists = []

    if (args.mute):
        muted_artists = set(map(lambda x: x.strip(),args.mute.split(",")))
    if (args.solo):
        solo_artits = set(map(lambda x: x.strip(),args.solo.split(",")))
        all_artists = set(map(lambda x: x.name, player.artists))
        muted_artists = list(all_artists - solo_artits) 



    if muted_artists:
        for a in player.artists:
            if a.name in muted_artists:
                a.settings.set_gain( a.settings.gain + args.mute_level )
                logging.debug(f"Setting gain for artist {a.name} to {a.settings.gain}dB.")

    if (args.tracks):
        player.add_track_callback(write_track_cb)

    score = Score.from_file(args.score)

    if (args.info):
        print_info(args, score, player)
        sys.exit()

    if (args.loop):
        score.loop(args.loop)

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
