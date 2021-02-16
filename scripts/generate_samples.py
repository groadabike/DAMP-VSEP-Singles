import pandas as pd
import json
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--root_dir', type=Path, required=True,
                    help='Full path to the DAMP-VSEP dataset')
parser.add_argument('--metadata_dir', type=Path, required=True,
                    help="Path to metadata directory")
parser.add_argument('--split', type=str, required=True,
                    help="Dataset to process")
parser.add_argument('--segment', type=float, default=3.0,
                    help='Segment length in seconds')
parser.add_argument('--shift', type=float, default=0.5,
                    help="Shift between examples in percentage")


def generate_singles_samples(df_chunks, df_metadata, segment, shift):
    samples = {}
    for index, row in df_chunks.iterrows():
        meta_perf = df_metadata[df_metadata.performance == row['performance']]
        start = row['start_time']
        time_consumed = 0.0
        contain_more_samples = True
        count = 0
        while contain_more_samples:
            if segment is None:
                contain_more_samples = False
                sample = {}
                sample['performance'] = row['performance']
                sample['vocal'] = row['path']
                sample['background'] = meta_perf.iloc[0]['background']
                sample['mixture'] = meta_perf.iloc[0]['original_mix']
                sample['vocal_start'] = float(f"{start:0.6f}") + float(
                    f"{float(meta_perf.iloc[0]['vocal_start']):0.6f}")
                sample['vocal_end'] = float(f"{row['end_time']:0.6f}") + float(
                    f"{float(meta_perf.iloc[0]['vocal_start']):0.6f}")
                sample['background_start'] = float(f"{start:0.6f}") + float(
                    f"{float(meta_perf.iloc[0]['background_start']):0.6f}")
                sample['background_end'] = float(f"{row['end_time']:0.6f}") + float(
                    f"{float(meta_perf.iloc[0]['background_start']):0.6f}")
                sample['mixture_start'] = sample['background_start']
                sample['mixture_end'] = sample['background_end']
                samples[f"{row['performance']}-{row['chunk']:03d}-{count:03d}"] = sample

            elif row['duration'] - time_consumed >= segment:
                time_consumed += segment * shift
                sample = {}
                sample['performance'] = row['performance']
                sample['vocal'] = row['path']
                sample['background'] = meta_perf.iloc[0]['background']
                sample['mixture'] = meta_perf.iloc[0]['original_mix']
                sample['vocal_start'] = float(f"{start:0.6f}") + float(f"{float(meta_perf.iloc[0]['vocal_start']):0.6f}")
                sample['vocal_end'] = float(f"{sample['vocal_start'] + segment:0.6f}")
                sample['background_start'] = float(f"{start:0.6f}") + float(f"{float(meta_perf.iloc[0]['background_start']):0.6f}")
                sample['background_end'] = float(f"{sample['background_start'] + segment:0.6f}")
                sample['mixture_start'] = sample['background_start']
                sample['mixture_end'] = sample['background_end']
                start = start + segment * shift
                samples[f"{row['performance']}-{row['chunk']:03d}-{count:03d}"] = sample
                count += 1
            else:
                if row['duration'] - time_consumed >= 1.0:
                    contain_more_samples = False
                    sample = {}
                    sample['performance'] = row['performance']
                    sample['vocal'] = row['path']
                    sample['background'] = meta_perf.iloc[0]['background']
                    sample['mixture'] = meta_perf.iloc[0]['original_mix']
                    sample['vocal_start'] = float(f"{row['end_time'] - segment:0.6f}") + float(
                        f"{float(meta_perf.iloc[0]['vocal_start']):0.6f}")
                    sample['vocal_end'] = float(f"{row['end_time']:0.6f}")
                    sample['background_start'] = float(f"{row['end_time'] - segment:0.6f}") + float(
                        f"{float(meta_perf.iloc[0]['background_start']):0.6f}")
                    sample['background_end'] = float(f"{row['end_time']:0.6f}")
                    sample['mixture_start'] = sample['background_start']
                    sample['mixture_end'] = sample['background_end']
                    samples[f"{row['performance']}-{row['chunk']:03d}-{count:03d}"] = sample

    return samples


def main(args):
    df_chunks = pd.read_csv(args.metadata_dir / f"{args.split}_chunks.csv")
    print(len(df_chunks))
    df_chunks = df_chunks[df_chunks.duration >= args.segment]
    print(len(df_chunks))
    noisy_samples = df_chunks[(df_chunks.start_time == 0.0) & (df_chunks.end_time == df_chunks.duration)]
    df_chunks = df_chunks[~((df_chunks.start_time == 0.0) & (df_chunks.end_time == df_chunks.duration))]
    print(len(df_chunks))

    meta_path = args.metadata_dir / f"{args.split}_sr16000.json"
    with open(meta_path, 'r') as mfile:
        jmeta = json.load(mfile)
    df_metadata = pd.DataFrame.from_dict(jmeta.values())
    df_metadata['performance'] = jmeta.keys()
    if args.split in ['test', 'valid']:
        segment = None
    else:
        segment = args.segment

    solos = generate_singles_samples(df_chunks, df_metadata, segment, args.shift)
    json.dump(solos, open(f'metadata/{args.split}_dataset.json', "w"), indent=2)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)