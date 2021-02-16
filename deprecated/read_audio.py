import subprocess as sp
from pathlib import Path
import json
import numpy as np


def _read_info(path):
    stdout_data = sp.check_output([
        'ffprobe', "-loglevel", "panic",
        str(path), '-print_format', 'json', '-show_format', '-show_streams'
    ])
    return json.loads(stdout_data.decode('utf-8'))


def _read_audio(path,
                filename,
                seek_time=None,
                duration=None,
                sample_rate=None,
                channels=None):
    if duration is None:
        target_size = None
        query_duration = None
    else:
        target_size = int(sample_rate * duration)
        query_duration = float((target_size + 1) / sample_rate)

    command = ['ffmpeg', '-y']
    command += ['-loglevel', 'panic']
    if seek_time:
        command += ['-ss', str(seek_time)]
    command += ['-i', path]

    if query_duration is not None:
        command += ['-t', str(query_duration)]
    command += ['-f', 'f32le']
    if sample_rate is not None:
        command += ['-ar', str(sample_rate)]
    command += ['-ac', '2']
    command += [filename]

    sp.run(command, check=True)
    wav = np.fromfile(filename, dtype=np.float32)




class AudioFile:
    def __init__(self, perf, details):
        self.perf = perf
        self.vocal = details['vocal']
        self.back = details['background']
        self.mix = details['original_mix']

        self.original_mean = details['original_mix_mean']
        self.original_std = details['original_mix_std']

        self.mean = details['mix_mean']
        self.std = details['mix_std']

        self.duration = details['duration']
        self.vocal_start = details['vocal_start']
        self.background_start = details['background_start']

        self.scaler = details['scaler']




