# About this repository

This repository shares code to construct a pre-processed version of DAMP-VSEP dataset for single ensemble vocal separation, i.e., duets performances will be discarded. This code will realign the sources by using cross-correlation. The data must be obtained in advance by going to https://zenodo.org/record/3553059#.X38Y_nVKhhE and requesting Smule's Research Team access to it.   


# Overview of DAMP-VSEP

The DAMP-VSEP dataset is a corpus constructed for karaoke vocal separation task. It is composed of 41000 30-seconds length song segments from 6456 singers and 11494 song arrangements. For each song segment, it provides the vocal performance **v**, the corresponding backtracking **b** and a mixture of the two **x**. The recordings correspond to performances from 155 countries and 36 different languages. About the half of the song segments correspond of duet ensembles where each vocal segment is provided in independent audio files. 

# Pre-processing procedure

This repository construct a dataset for single ensemble vocal separation as part of a English lyrics transcription task. This means that the evaluation set constructed is comformed only by English spoken song so it can be use for recognition evaluation as well.

###1. English spoken training subset(9243 audio recording / ~77 hrs)

Subset constructed utilising all English spoken songs. This subset is conformed of 4607 solo ensemble and 3842 duets. Duets are split into two independent single performances. This allows to utilise the duets instead of discarding these recordings. Converting the duets into single performances invalidate the mixture as some duets may be overlap, forcing to re-mixed the vocal with the background.

To avoid overlap between the training and test sets, all identical backgrounds were group by using their MD5 checksum. Then, cross-correlation between all the distinct backgrounds was used to group all perceptually similar ones. This last step was necessary because several non-identical backgrounds, i.e., with different checksum, are slightly different versions of the same recording. This process resulted in 1364 clusters. The development and evaluation sets were constructed by selecting, and equally distributing, 200 backgrounds from the clusters with a single element. Further, the evaluation set was aligned and transcribed at the utterance level.


###2. Singles ensembles training subset(20660 performances / ~170 hrs)

Subset utilised all solo ensemble for training data, regardless of the language. However, to enable the utilisation of the provided mixture, all English duets were discarded in this version, reducing the English language samples to 4407.


###3. Validation and Evaluation Subsets (100 performaces / ~ 0.8 hrs  each)

200 single ensemble Englis spoken performances (100 each) obtained after construction of English subset.


# Citing DAMP-VSEP

```
@misc{DampVsep,
  author = {{Smule, Inc.} (2019)},
	title =  {{DAMP-VSEP: Smule Digital Archive of Mobile Performances - Vocal Separation (Version 1.0.1) [Data set]}}, 
	note = {Zenodo. http://doi.org/10.5281/zenodo.3553059}
}
```
