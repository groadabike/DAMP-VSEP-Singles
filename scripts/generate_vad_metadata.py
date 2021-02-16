from pathlib import Path
from find_speech_segments import find_speech_segments
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool
from functools import partial
import argparse
import json


parser = argparse.ArgumentParser()
parser.add_argument(
    "--root_dir", type=Path, required=True, help="Full path to the DAMP-VSEP dataset"
)
parser.add_argument("--split", type=str, required=True, help="Dataset to process")
parser.add_argument(
    "--metadata_dir", type=Path, required=True, help="Path to metadata directory"
)


def main(args):
    meta_path = args.metadata_dir / f"{args.split}_sr16000.json"
    with open(meta_path, "r") as mfile:
        jmeta = json.load(mfile)
    meta = pd.DataFrame.from_dict(jmeta.values())
    meta["performance"] = jmeta.keys()

    vocal_audios = [
        row
        for i, row in meta.iterrows()
        #if row["performance"] == "1003628485_2895771714"
    ]
    pool = Pool(processes=12)
    func = partial(find_speech_segments, 3, args.root_dir)
    list_chunks = []

    for result in tqdm(
        pool.imap_unordered(func, vocal_audios), total=len(vocal_audios)
    ):
        compress_results = []
        cur_chunk = None
        for res in result:
            if cur_chunk is None:
                cur_chunk = res
            else:
                #  min 500ms of silence between chunks
                #  otherwise, join the chunks
                if res["start_time"] - cur_chunk["end_time"] <= 0.5 and (
                    res["duration"] < 3.0 or cur_chunk["duration"] < 3.0
                ):
                    cur_chunk["end_time"] = res["end_time"]
                    cur_chunk["duration"] = (
                        cur_chunk["end_time"] - cur_chunk["start_time"]
                    )

                else:
                    compress_results.append(cur_chunk)
                    cur_chunk = res

        if cur_chunk is not None:
            compress_results.append(cur_chunk)
        list_chunks += compress_results

    df = pd.DataFrame.from_dict(list_chunks)
    df.to_csv(f"{args.metadata_dir}/{args.split}_chunks.csv", index=False)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
