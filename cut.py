from pydub import AudioSegment
from pydub import effects
from pydub.playback import play
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(
                    prog = 'Cut out an prepare samples',
                    description = 'Prepare samples.')
parser.add_argument('input', type=Path, help="The path to bataria files.")           # positional argument
parser.add_argument('start', type=int, help="Start position of sample in milliseconds")           # positional argument
parser.add_argument('beat', type=int, help="Position of beat in milliseconds")           # positional argument
parser.add_argument('stop',  type=int, help="stop position for this beat. ")           # positional argument
parser.add_argument('output', type=Path, help="pout filename")           # positional argument
parser.add_argument('-i', '--fade_in', type=int, default=15 )  # on/off flag
parser.add_argument('-f', '--fade_out', type=int, default=15)  # on/off flag
parser.add_argument('-n', '--normalize', type=float, default=1.0)  # Normalize input
parser.add_argument('-b', '--bitrate', type=int, default=48000) 


def main(args):
    audio_data = AudioSegment.from_file(args.input)
    # check for mono!

    if args.normalize:
       audio_data.normalize(args.normalize)


    print("playing segment")
   
    segments = [
        (  620,  629, 1082 ),
        ( 1082, 1097, 1564 ),
        ( 1564, 1579, 2046 ),
        ( 2540, 2555, 3018 ),
        ( 3018, 3033, 3503 ),
        ( 3503, 3518, 4008 )

            ]

    for idx, seg in zip( range(len(segments)), segments):
        start_idx, beat_idx, stop_idx = seg
        segment = audio_data[ start_idx: stop_idx ].fade_in(args.fade_in).fade_out(args.fade_out)
        play(segment)
        outfilename = str(args.output).format(idx)
        segment.export( outfilename, format="wav", bitrate=args.bitrate, tags={ "desc" : "abc" })
        print(f"{outfilename};offset={ beat_idx - start_idx}")
    


if __name__ == "__main__":
    _LOG_FMT="%(levelname)s: %(message)s"
    args = parser.parse_args()
    main(args)




