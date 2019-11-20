## Installation

This work relies on [pyannote-audio](https://github.com/pyannote/pyannote-audio), a python library gathering all the neural building blocks required for building speaker diarization models. 
In particular, we focused on solving one of the earliest step of the diarization pipeline : the speech activity detection task !

The installation consist of creating a new conda environment where we will install [pyannote-audio](https://github.com/pyannote/pyannote-audio).

```bash
# First, let's clone this repo
$ git clone https://github.com/hbredin/DomainAdversarialVoiceActivityDetection.git
$ cd DomainAdversarialVoiceActivityDetection

# create a conda environment with Python 3.6 or later
$ conda create --name pyannote python=3.6
$ source activate pyannote

# install pytorch following official instructions from https://pytorch.org/

# install from source in the "develop" branch
$ git clone https://github.com/pyannote/pyannote-audio.git
$ cd pyannote-audio
$ git checkout develop
$ pip install .
``` 

Now that the environment has been set up, we can prepare the data by following [these instructions](./database.md).