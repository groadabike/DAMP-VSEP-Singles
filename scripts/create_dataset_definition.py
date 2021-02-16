import argparse
import pandas as pd
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from pathlib import Path
import json
import librosa

from utils import get_amplitude_scaling_factor, xcorr_searcher_max, load_data

# Filter out performances shorter than ```MIN_DURATION``` secs
MIN_DURATION = 15.0

# Filter out songs with mixtures shorter than vocal in %
# These are errors in the dataset
DURATION_VAR = 0.95

# Framing parameters for RMS
NHOP = 0.010
WIN = 0.025

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--split', type=str, required=True,
                    help='Dataset to process')
parser.add_argument('--root_path', type=str, required=True,
                    help='Root path to DAMP-VSEP')
parser.add_argument('--sample_rate', type=int, required=True,
                    default=16000)
parser.add_argument('--output_meta_path', type=str, required=True,
                    help='Path where save the metadata')


def main(args):
    metadata_path = Path(args.output_meta_path)
    track_list = pd.read_csv(f"split/{args.split}.csv")

    metadata = []
    pool = Pool(processes=cpu_count())
    track_inputs = [(t, Path(args.root_path), args.sample_rate)
                    for i, t in track_list.iterrows()]
    for meta in tqdm(pool.imap_unordered(build_metadata, track_inputs),
                     total=len(track_inputs)):
        if meta:
            metadata.append(meta)
    tracks = {p: m for p, m in metadata}
    metadata_path.mkdir(parents=True, exist_ok=True)
    json.dump(tracks, open(metadata_path / f"{args.split}_sr{args.sample_rate}.json",
                           'w'),
              indent=2)


def build_metadata(inputs):
        track, root, sample_rate = inputs
        hop_length = int(sample_rate * NHOP)
        frame_length = int(sample_rate * WIN)
        vocal = load_data(root / track['vocal_path'],
                          sample_rate=sample_rate)

        # Discard silence vocal target
        if vocal.sum() == 0.0:
            print(f"Track {track['perf_key']} is silence - discarded")
            return None

        # Get original duration to discard short vocal target
        vocal_dur = librosa.get_duration(vocal, sr=sample_rate)
        if vocal_dur < MIN_DURATION:
            print(f"Track {track['perf_key']} too short ({vocal_dur} sec) - discarded")
            return None

        ori_mix = load_data(root / track['mix_path'],
                            sample_rate=sample_rate)

        ori_mix_dur = librosa.get_duration(ori_mix, sr=sample_rate)
        if ori_mix_dur < vocal_dur * DURATION_VAR:
            print(f"Mixture {track['perf_key']} length ({ori_mix_dur}) is shorter than vocal length ({vocal_dur}) - discarded")
            return None

        # Get vocal shifting by doing several xcorr of small segments of vocal.
        # The shifting time determine the start point of background and vocal.
        vocal_shift = xcorr_searcher_max(ori_mix, vocal, sample_rate, frame_length, hop_length)

        if vocal_shift <= 0:
            vocal_start = abs(vocal_shift)
            back_start = 0
        else:
            vocal_start = 0
            back_start = vocal_shift

        # Get new/real min duration.
        back = load_data(root / track['background_path'],
                         sample_rate=sample_rate)

        vocal = vocal[int(vocal_start * sample_rate):]
        back = back[int(back_start * sample_rate):]

        vocal_dur = librosa.get_duration(vocal, sr=sample_rate)
        back_dur = librosa.get_duration(back, sr=sample_rate)
        min_dur = min(vocal_dur, back_dur)

        # Create mixture to calculate mean and std
        mix = vocal[:int(min_dur * sample_rate)] + back[:int(min_dur * sample_rate)]

        # Get amplitude for SNR=0
        amplitude_scaler = get_amplitude_scaling_factor(vocal, back)

        track_info = dict()
        track_info['original_mix'] = track['mix_path']
        track_info['original_mix_mean'] = \
            f"{ori_mix[int(back_start * sample_rate):int(min_dur * sample_rate)].mean()}"
        track_info['original_mix_std'] = \
            f"{ori_mix[int(back_start * sample_rate):int(min_dur * sample_rate)].std()}"
        track_info['mix_mean'] = f"{mix.mean()}"
        track_info['mix_std'] = f"{mix.std()}"
        track_info['duration'] = f"{min_dur}"

        track_info['vocal'] = track['vocal_path']
        track_info['vocal_start'] = f"{vocal_start}"
        track_info['scaler'] = f"{amplitude_scaler:}"

        track_info['background'] = track['background_path']
        track_info['background_start'] = f"{back_start}"

        return track['perf_key'], track_info


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
