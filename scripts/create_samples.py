import json
import librosa
from pathlib import Path
import soundfile as sf
import warnings
warnings.filterwarnings('ignore')

df = json.load(open("metadata/valid_dataset.json", 'r'))
root_path = Path('/media/gerardo/TOSHIBA/DataSets/DAMP/DAMP-VSEP')
dest_root = Path('/media/gerardo/TOSHIBA/DataSets/DAMP/DAMP-VSEP_samples')
for index in df.keys():
    wav, sr = librosa.load(str(root_path / df[index]['vocal']),
                           offset=df[index]['vocal_start'],
                           duration=df[index]['vocal_end'] - df[index]['vocal_start'],
                           sr=16000)

    path = dest_root / Path(df[index]['vocal']).parent / f"{index}_vocal.wav"
    path.parent.mkdir(exist_ok=True, parents=True)
    sf.write(path, wav, sr)

    wav, sr = librosa.load(str(root_path / df[index]['background']),
                           offset=df[index]['background_start'],
                           duration=df[index]['background_end'] - df[index]['background_start'],
                           sr=16000)

    path = dest_root / Path(df[index]['background']).parent / f"{index}_background.wav"
    path.parent.mkdir(exist_ok=True, parents=True)
    sf.write(path, wav, sr)

    wav, sr = librosa.load(str(root_path / df[index]['mixture']),
                           offset=df[index]['mixture_start'],
                           duration=df[index]['mixture_end'] - df[index]['mixture_start'],
                           sr=16000)

    path = dest_root / Path(df[index]['mixture']).parent / f"{index}_mixture.wav"
    path.parent.mkdir(exist_ok=True, parents=True)
    sf.write(path, wav, sr)


