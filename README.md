# Domain Adversarial Voice Activity Detection

## Installation

Start by creating a new conda environment where we will install [pyannote-audio](https://github.com/pyannote/pyannote-audio).

```bash
# create a conda environment with Python 3.6 or later
$ conda create --name da-pyannote python=3.6
$ source activate da-pyannote

# install pytorch following official instructions from https://pytorch.org/

# install from source in the "develop" branch
$ git clone https://github.com/pyannote/pyannote-audio.git
$ cd pyannote-audio
$ git checkout develop
$ pip install .
```

## Database creation

Once the conda environment has been installed, the next step consists of building the database with all the information we need
for performing domain-adversarial speech activity detection. This step is described in this [jupyter notebook](./database.ipynb).

## Running experiments

TO DO TO DO TO DO
