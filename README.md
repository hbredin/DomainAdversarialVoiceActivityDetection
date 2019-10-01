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

Once you succesfully ran the notebook [database.ipynb](./database.ipynb) of the "Database creation" step, you can first create a configuration file describing all the hyper-parameters of your model :

```bash
cat models/config.yml
```

```yaml
task:
   name: DomainAdversarialSpeechActivityDetection
   params:
      duration: 2.0      # sequences are 2s long
      batch_size: 64     # 64 sequences per batch
      domain: domain
      attachment: 0
      per_epoch: 1       # one epoch = 1 day of audio
      alpha: 0.01
      domain_loss: MSELoss
      rnn:
         unit: LSTM
         hidden_size: 128
         num_layers: 1
         bidirectional: False
         pool: max

data_augmentation:
   name: AddNoise                                   # add noise on-the-fly
   params:
      snr_min: 10                                   # using random signal-to-noise
      snr_max: 20                                   # ratio between 10 and 20 dBs
      collection: MUSAN.Collection.BackgroundNoise  # use background noise from MUSAN
                                                    # (needs pyannote.db.musan)
feature_extraction:
   name: RawAudio      # use MFCC from librosa
   params:
     sample_rate: 16000

architecture:
   name: pyannote.audio.models.PyanNet
   params:
     rnn:
        unit: LSTM
        hidden_size: 128
        num_layers: 2
        bidirectional: True
     ff:
        hidden_size: [128, 128]     

scheduler:
   name: CyclicScheduler        # use cyclic learning rate (LR) scheduler
   params:
      learning_rate: auto       # automatically guess LR upper bound
      epochs_per_cycle: 14      # 14 epochs per cycle
```

Most of these parameters are described in the [pyannote-audio](https://github.com/pyannote/pyannote-audio) repository.
The parameter **domain_loss** indicates the loss you would like to use for the domain adversarial branch, implemented options are [MSELoss, NLLLoss].
The parameter **alpha** is the weight associated to this loss.
The parameter **attachment** controls where the domain adversarial branch is plugged in the main architecture. 
- 0 corresponds to the last layer of the SincNet part. 
- 1 corresponds to a branching right after the first LSTM.
- 2 corresponds to a branch right after the second LSTM.

Before launching train/dev/apply, don't forget to set the variable `PYANNOTE_DATABASE_CONFIG` to where your `database.yml` file is. 

```bash
export PYANNOTE_DATABASE_CONFIG="{ROOT}/database.yml"
```

Once the configuration file has been created, one can run a training by typing :

```bash
pyannote-speech-detection train --gpu --to=200 models X.SpeakerDiarization.AMI_LeaveOneDomainOut_E
```

Develop :

```bash
pyannote-speech-detection validate --gpu models X.SpeakerDiarization.AMI_LeaveOneDomainOut_E
```

Apply :

```bash
pyannote-speech-detection apply --gpu models/train/X.SpeakerDiarization.AMI_LeaveOneDomainOut_E.train/validate/X.SpeakerDiarization.AMI_LeaveOneDomainOut_E.development X.SpeakerDiarization.AMI_LeaveOneDomainOut_E
```

The protocols used as arguments respect the following naming convention **X.SpeakerDiarization.{CORPORA}_LeaveOneDomainOut_{DOMAIN}**, with :
- {CORPORA} amongst [AMI,DIHARD]
- {DOMAIN} amongst [E, I, T] for AMI
- {DOMAIN} amongst [audiobooks, broadcast_interview, child, clinical, court, maptask, meeting, restaurant, socio_field, socio_lab, webvideo] for DIHARD.

Note that the specified domain is the one that will be held out. If X.SpeakerDiarization.AMI_LeaveOneDomainOut_E is chosen for training, developping and testing the model,
that means that we'll train and develop on all the other subsets (i.e. I and T), and we'll test on E.
