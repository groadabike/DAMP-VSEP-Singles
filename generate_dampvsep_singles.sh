#!/bin/bash
set -eu  # Exit on error

damvsep_root=$1
output_dir=$2
python_path=$3
sample_rate=16000

splits="test valid train_english train_singles"

for split in $splits; do
  $python_path scripts/create_metadata.py --split $split \
    --root_path $damvsep_root \
    --sample_rate $sample_rate \
    --output_meta_path $output_dir
done

