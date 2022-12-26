import yaml
import logging
import logging
import glob
from pathlib import Path

from .utils import TimeSignature, Clock
from .instrument import Instrument
from .sample     import Sample
from .sample_builder import SampleBuilder
from .pattern import parse_pattern

def _required(dic, key, type=str):
    return type(dic[key])


class Bateria():
    def __init__(self, name, bpm):
        self._name = name
        self._instruments = {}
        self._bpm = int(bpm)
        self._base_dir = None

    @property
    def instruments(self):
        return list(self._instruments)
    
    def instrument(self, name):
        return self._instruments[name]
    
    @property
    def bpm(self):
        return self._bpm
    
    @property
    def frame_rate(self):
        return 48000

    @staticmethod
    def from_file(filename):
        cfg = {}
        filename = Path(filename)
        with open(filename, "r") as fin:
            cfg = yaml.safe_load(fin)
        #logging.debug(repr(cfg))
        bat = Bateria(cfg["name"], _required(cfg, "bpm", int))
        bat._base_dir = filename.parent 
        bat._parse_config(cfg)
        return bat

    def _parse_pattern(self, cfg, instrument, pattern_cfg):
        pattern = instrument.add_pattern(_required(pattern_cfg, "pattern"))
        logging.debug(f'Adding pattern "{pattern}" for instrument {instrument.name}.')
        for alias in pattern_cfg.get("aliases",[]):
            logging.debug(f'Adding alias "{alias}" to pattern "{pattern}" for instrument {instrument.name}.')
            pattern.alias(alias)
        for sample in _required(pattern_cfg, "samples", list):
            if "*" in sample:
                for name in glob.glob( str(self._base_dir / sample)):
                    logging.debug(f"Adding sample '{name}' to pattern {pattern}")
                    pattern.add_samples(Sample( name))
                pass
            else:
                logging.debug(f"Adding sample {sample} to pattern {pattern} for instrument {instrument.name}.")
                pattern.add_samples(Sample( str( self._base_dir / sample)))

        if (not len(pattern.samples)):
            raise RuntimeError(f"No samples found for pattern \"{pattern}\" and instrument {instrument}.")
        pass

    def _parse_patterns(self, cfg, instrument_cfg, instrument):
        for pattern_cfg in instrument_cfg.get("patterns", []):
            self._parse_pattern(cfg, instrument, pattern_cfg)
            
    def _parse_cliche(self, cfg, cliche_cfg, instrument):
        pattern = instrument.add_pattern(_required(cliche_cfg, "pattern"))
        logging.debug(f'Adding cliche "{pattern}" for instrument {instrument.name}.')
        
        for alias in cliche_cfg.get("aliases",[]):
            logging.debug(f'Adding alias "{alias}" to cliche "{pattern}" for instrument {instrument.name}.')
            pattern.alias(alias)

        # 1. pass: build the smaple!
        sb = SampleBuilder(self.bpm, self.frame_rate)
        reciept_str = cliche_cfg["reciept"]
        for re in reciept_str.split(";"):
            pat, shift = re.split(":")[0:2]
            pat = parse_pattern(pat)
            shift = str(shift)
            options = re.split(":")[2:]
            patterns = sorted(
                    filter(
                        lambda x: x.pattern == pat.pattern and x.on_beat_1 == pat.on_beat_1 and not x.cliche, 
                        instrument),  key=lambda x: x.score)
            if (not patterns):
                raise RuntimeError(f"Could not find a pattern for \"{pat}\" to build cliche \"{pattern}\" for instrument {instrument}")
            # if we have more than one pattern, something is wrong! Take the first one.
            pat = patterns[0]
            sb.add_subsample( pat.sample(), shift )
        # 2. Add the pattern!
        pattern.add_samples(sb.build())


        #SampleBuilder(100, 48000)
        #        .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"))
        #        .add_subsample(Sample("samples/estácio/100bpm/caixa-x___-1.wav"), ".x")
        #        .build()
        #        )


        pass

    def _parse_cliches(self, cfg, instrument_cfg, instrument):
        for cliche_cfg in instrument_cfg.get("cliches", []):
            self._parse_cliche(cfg, cliche_cfg, instrument)
        # parse auto cliches
        AUTO_CLICHES = {
                ".x..": { "reciept": "x:.x..",             "aliases" : [] },
                "..x.": { "reciept": "x:..x.",             "aliases" : [".x"] },
                "...x": { "reciept": "x:...x",             "aliases" : [] },
                "xx..": { "reciept": "x:x;x:.x..",         "aliases" : [] },
                "x.x.": { "reciept": "x:x;x:..x.",         "aliases" : ["xx"] },
                "x..x": { "reciept": "x:x;x:...x",         "aliases" : [] },
                "xxx.": { "reciept": "x:x;x:.x..;x:..x.",  "aliases" : [] },
                "xx.x": { "reciept": "x:x;x:.x..;x:...x",  "aliases" : [] },
                ".xxx": { "reciept": "x:.x..;x:.x;x:...x", "aliases" : [] },
                "x.xx": { "reciept": "x:x;x:..x.;x:...x",  "aliases" : [] },
                ".x.":  { "reciept": "x:.x.",              "aliases" : [] },
                "..x":  { "reciept": "x:..x",              "aliases" : [] },
                "xx.":  { "reciept": "x:x;x:.x.",          "aliases" : [] },
                ".xx":  { "reciept": "x:.x.;x:..x",        "aliases" : [] },
                "x.x":  { "reciept": "x:x;x:..x",          "aliases" : [] },
                "xxx":  { "reciept": "x:x;x:.x.;x:..x",    "aliases" : [] },
                }
        auto_cliches = instrument_cfg.get("auto_cliches", [])
        if True is auto_cliches:
            auto_cliches = AUTO_CLICHES.keys()
        if auto_cliches:
            for ac in auto_cliches:
                skip = False
                for pat in instrument:
                    if pat.pattern == parse_pattern(ac).pattern: 
                        skip = True
                        break
                if skip:
                    logging.debug(f"Skipping auto generated cliche \"{ac}\".")
                    continue

                # check, that a given pattern is not already configured 
                self._parse_cliche(cfg, { "pattern" : ac, **AUTO_CLICHES[ac] }, instrument)
                pass


    def _parse_instrument(self, cfg, instrument_cfg):
        instrument = Instrument(_required(instrument_cfg, "name"), 
                bpm = _required(cfg, "bpm"))
        self._parse_patterns(cfg, instrument_cfg, instrument)
        self._parse_cliches(cfg, instrument_cfg, instrument)
        return instrument
        

    def add_instrument(self, instrument):
        logging.debug(f"Adding instrument {instrument.name}.")
        self._instruments[ instrument.name ] = instrument
        return instrument

    def _parse_instruments(self, cfg):
        for instrument_cfg in cfg.get("instruments", []):
            instrument = self._parse_instrument(cfg, instrument_cfg)
            self.add_instrument(instrument)    

    def _parse_config(self, cfg):
        self._parse_instruments(cfg)
     
