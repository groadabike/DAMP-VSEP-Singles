#!/bin/bash
set -eu  # Exit on error

damvsep_root=/media/gerardo/TOSHIBA/DataSets/DAMP/DAMP-VSEP
metadata_dir=metadata
python_path=python
sample_rate=16000
stage=2

splits="test valid train_english train_singles"


if [ $stage -le 1 ]; then
  # Find real start and end point using cross-correlation
  for split in $splits; do
    $python_path scripts/create_dataset_definition.py --split $split \
      --root_path $damvsep_root \
      --sample_rate $sample_rate \
      --output_meta_path $metadata_dir
  done
fi

if [ $stage -le 2 ]; then
  # Use VAD to detect vocal segments
  for split in $splits; do
    $python_path scripts/generate_vad_metadata.py --split $split \
      --root_dir $damvsep_root \
      --metadata_dir $metadata_dir
  done
fi

if [ $stage -le 0 ]; then
  # Use VAD to detect vocal segments
  for split in $splits; do
    echo "Creating ${split}_dataset.csv"
    $python_path scripts/generate_samples.py --split $split \
      --root_dir $damvsep_root \
      --metadata_dir $metadata_dir \
      --segment 3.0 \
      --shift 0.5
  done
fi


