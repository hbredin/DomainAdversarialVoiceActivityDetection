## Running experiments

#### Understanding what's going on

###### Configuration file
Once you succesfully ran the notebook [database.ipynb](./database.ipynb) of the "Database creation" step, you can first have a look at the configuration file describing all the hyper-parameters of your model :

```bash
cat models/config.yml
```

```yaml
task:
   name: DomainAdversarialSpeechActivityDetection
   params:
      duration: 2.0         # sequences are 2s long
      batch_size: 64        # 64 sequences per batch
      domain: domain
      attachment: 0         # indicates that the domain adversarial branch should be plugged straight after sincnet
      per_epoch: 1          # one epoch = 1 day of audio
      alpha: 0.01           # the weight associated to the domain loss - called lambda in the paper -
      domain_loss: MSELoss  # the domain loss, should be in [MSELoss, NLLLoss]
      rnn:                  # describes the architecture of the domain adversarial branch
         unit: LSTM
         hidden_size: 128
         num_layers: 1
         bidirectional: False     # unidirectional
         pool: max                # apply max temporal pooling

data_augmentation:
   name: AddNoise                                   # add noise on-the-fly
   params:
      snr_min: 10                                   # using random signal-to-noise
      snr_max: 20                                   # ratio between 10 and 20 dBs
      collection: MUSAN.Collection.BackgroundNoise  # use background noise from MUSAN
                                                    # (needs pyannote.db.musan)
                                                    
feature_extraction:
   name: RawAudio                                   # indicates that we want to work from raw waveform directly
   params:
     sample_rate: 16000

architecture:                                       # describes the architecture of the main branch
   name: pyannote.audio.models.PyanNet
   params:
     rnn:
        unit: LSTM
        hidden_size: 128
        num_layers: 2
        bidirectional: True
     ff:
        hidden_size: [128, 128]     

callbacks:
      - name: pyannote.audio.train.domain_loss_scheduler.DomainLossScheduler
        params:
          lower: 0              # the initial value of alpha
          higher: 10            # the value that alpha must reach
          start: 0              # the epoch from which we need to start the growth
          end: 150              # the epoch after which we need to stop the growth
          growth: linear        # indicates the growth that needs to be adopted, must belong to ['linear', 'exponential']

scheduler:
   name: CyclicScheduler        # use cyclic learning rate (LR) scheduler
   params:
      learning_rate: auto       # automatically guess LR upper bound
      epochs_per_cycle: 14      # 14 epochs per cycle
```

Most of these parameters are described in the [pyannote-audio](https://github.com/pyannote/pyannote-audio) repository.
Those are exactly the ones we used in the paper.

###### Pyannote protocols

Before running any experiments, you must set the variable `PYANNOTE_DATABASE_CONFIG` to where your `database.yml` file is, so that the system knows where to find the DIHARD dataset : 

```bash
export PYANNOTE_DATABASE_CONFIG="{ROOT}/database.yml"
```

where *{ROOT}* is the folder where this git repository has been installed.
This file contains all the protocols that [pyannote-audio](https://github.com/pyannote/pyannote-audio) needs to know where and how to access the data.

A *pyannote protocol* is an entity describing where and how to access the files. Most notably, it stipulates the train/dev/test split.
Hence, **X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks** corresponds to :
- A train/dev on all of the DIHARD subdomains, except the *audiobooks* one.
- A test on the *audiobooks* domain only.

You can replace *audiobooks* by any of the domain belonging to *[broadcast_interview, child, clinical, court, maptask, meeting, restaurant, socio_field, socio_lab, webvideo]*.
You can also choose to train, develop and test your model on all of the domains of DIHARD at once by using the **X.SpeakerDiarization.DIHARD_Official** protocol.


#### Training, developping, and testing a model

Make sure your pyannote environment has been activated before running any of these commands.
One can run a training by typing :

```bash
pyannote-audio sad train --gpu --to=200 models X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks
```

Where : 
- "**--to 200**" indicates the number of epochs during which we need to train the model.
- "**models**" is the folder where the *config.yml* is stored, and where the model will be created.
- "**X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks**" is the protocol you want to use.

This will create a model for each epoch in the **models** folder.

Similarly, you can develop your model by typing :

```bash
pyannote-audio sad validate --gpu models/train/X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks.train X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks
```

where : 
- "**models/train/X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks.train**" corresponds to the folder where your models, generated by the training step, have been stored.
- "**X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks**" is the protocol you want to validate on.

This step consists of computing a treshold, for each epoch, and from which the model decides if a particular frame contains speech or not.
The treshold associated to the best epoch is stored in the tree of the **models** folder.

Finally, one can check a model's final performances by typing :

```bash
pyannote-audio sad apply --gpu models/train/X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks.train/validate/X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks.development X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks
```

where :
- "**models/train/X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks.train/validate/X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks.development**" corresponds to the location of the best model
- "**X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_audiobooks**" is the protocol you want to use for testing.
