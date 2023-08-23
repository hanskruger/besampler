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
parser.add_argument('-P', '--debug_programm', default=None, help="Print the programm for a given artist and exit.")  # on/off flag
parser.add_argument('--count_in', action='store_true')  # on/off flag
parser.add_argument('--click', action='store_true')  # on/off flag
parser.add_argument('--info', action='store_true', help="print score info and exit")
parser.add_argument('--tracks', action='store_true')
parser.add_argument('--bpm', default=None, type=float, help="The output speed")
parser.add_argument('-f', '--format', default="mp3", help='format of output (wav|mp3)')  # on/off flag
parser.add_argument('--ensamble', help='Specify, which ensamble to use.')  # on/off flag
parser.add_argument('--script', help='Specify the range to be played.')  # on/off flag
parser.add_argument('--tex', action='store_true', help='Enabling tex parsing mode.')  # on/off flag

parser.add_argument('--mute', help='Mute the given aritsts.')  # on/off flag
#parser.add_argument('--mute_staff', help='Mute all artists of the given staff.')  # on/off flag
#parser.add_argument('--mute_instrument', help='Mute all artist of the given instruments.')  # on/off flag
parser.add_argument('--mute_level', default=-60.0, type=float, help='Amount in dB, by which artitsts should be muted.')  # on/off flag

parser.add_argument('--solo', help='Only play the artists listed.')  # on/off flag
#parser.add_argument('--solo_staff', help='Only play the artists playing a given staff.')  # on/off flag
#parser.add_argument('--solo_instrument', help='Only play the artists playinf the given instruments.')  # on/off flag

parser.add_argument('--loop', default=1, type = int, help='Number of times a given score should be played.')
parser.add_argument('--playset', type = str, help='Playset')


def click():
    ins = Instrument("Click", bpm = 100)
    ins.add_pattern("X").add_samples(
            Sample("samples/click-hard.wav"))
    ins.add_pattern("x").add_samples(
            Sample("samples/click-soft.wav"))
    return ins

def print_info(args, score, player, bateria, ensamble):
    MSG= f"""# Info about score and player
score.filename:       {args.score}
score.time.signature: {score.time_signature.pulses}/{score.time_signature.note_value}
score.staffs:         {", ".join(map(str, score.staffs))}
player.bpm:           {player.bpm}
player.instruments:   {", ".join(map(str, player.instruments))}
player.artists:       {", ".join(map(lambda x: x.name, player.artists))}
bateria.ensambles:    {", ".join(map(lambda x: x.name, bateria.ensambles))}
ensamble.name:        {ensamble.name}
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

    if not args.bpm:
        args.bpm = bateria.bpm

    if (bateria.bpm > args.bpm):
        raise RuntimeError(f"Requested speed {args.bpm} is bellow bateria speed ({bateria.bpm}), which is not support.")
    

    player = Player(bpm = bateria.bpm)

    # load ensamble
    ensamble = next(iter(bateria.ensambles))
        
    for artist in ensamble.artists:
        player.add_artist(artist.name, staff=artist.staff_name, instrument=bateria.instrument( artist.instrument_name)).set_pan( artist.pan).set_gain(artist.gain)

    if ("Count In" not in map(lambda x:x.staff_name, ensamble.artists)):
        player.add_artist("count_in", staff="Count In", instrument=click())
    if ("Click" not in map(lambda x:x.staff_name, ensamble.artists)):
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

    if (args.tex):
        score = Score.from_file(args.score, "TEX")
    else:
        score = Score.from_file(args.score)

    if (args.info):
        print_info(args, score, player, bateria, ensamble)
        sys.exit()

    if (args.playset):
        score.playset(args.playset)
    
    if (args.loop):
        score.loop(args.loop)

    if(args.count_in):
        score.add_count_in()

    if(args.click):
        score.add_click()
    
    if(args.debug_programm):
        def print_programm(prog, artist, score):
            print(artist)
            for e in prog[0]:
                print(e)
            pass
        player.add_prog_callback(print_programm)
        player.synthesize(score, staff= args.debug_programm)
        return True

    if (args.script):
        player._script = list(range(int(args.script), score.length))


    snd = player.synthesize(score)

    if (args.bpm > player.bpm):
        snd.speedup( args.bpm / player.bpm)
    
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
