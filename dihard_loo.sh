#!/usr/bin/env bash
source activate pyannote

if [ $# -ne 2 ]; then
    echo "Usage :"
    echo "./dihard_loo.sh min max"
    echo "Run all experiments whose index belongs to [min,max]"
    echo "Example :"
    echo "./dihard_loo.sh 0 5"
    echo "Run the first 5 experiments."
    exit
fi

MIN=$1
MAX=$2

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${THIS_DIR}

export PYANNOTE_DATABASE_CONFIG=${THIS_DIR}/database.yml
FOLDER=models
mkdir -p $FOLDER

if [ ! -f ./template_config.yml ]; then
	echo "Can't find template_config.yml in DomainAdversarialVoiceActivityDetection"
	exit
fi

DOMAINS=("audiobooks" "broadcast_interview" "child" "clinical" "court" "maptask" "meeting" "restaurant" "socio_field" "webvideo")
ALPHAS=("0" "0.001" "0.01" "0.1" "1")

# Create directory with config.yml containing the model parameters.
for alpha in ${ALPHAS[*]}; do
  EXPERIMENT_DIR=$FOLDER/${alpha//.}
  if [ ! -d $EXPERIMENT_DIR/train ]; then
    mkdir -p $EXPERIMENT_DIR/train
    cat template_config.yml | sed "s/\$TO_BE_REPLACED/$alpha/g" > $EXPERIMENT_DIR/config.yml
  fi
done
chmod -R 777 $FOLDER

var=0
for domain in ${DOMAINS[*]}; do
	PROTOCOL=X.SpeakerDiarization.DIHARD_LeaveOneDomainOut_$domain
	for alpha in ${ALPHAS[*]}; do

        EXPERIMENT_DIR=$FOLDER/${alpha//.}

        if [ "$var" -ge "$MIN" -a "$var" -lt "$MAX" ]; then

            # TRAINING
            if [ ! -d "$EXPERIMENT_DIR/train/${PROTOCOL}.train" ]; then
                echo "Submitting train n° $var"
                #qsub -j y -o loo_train_${PROTOCOL}_${alpha//.}.txt -l mem_free=64G -l ram_free=64G -l gpu=1 -l num_proc=2 train_sad.sh $EXPERIMENT_DIR $PROTOCOL
                #./train_sad.sh $EXPERIMENT_DIR $PROTOCOL
                #sleep 2
            fi

            # VALIDATION
            if [ ! -d "$EXPERIMENT_DIR/train/${PROTOCOL}.train/validate/${PROTOCOL}.development" ]; then
                echo "Submitting validation n° $var"
                #qsub -j y -o loo_dev_${PROTOCOL}_${alpha//.}.txt -l mem_free=64G -l ram_free=64G -l gpu=1 -l num_proc=2 validate_sad.sh $EXPERIMENT_DIR $PROTOCOL
                ./validate_sad.sh $EXPERIMENT_DIR $PROTOCOL
                sleep 2
            fi

            # TEST
            if [ ! -f "$EXPERIMENT_DIR/train/${PROTOCOL}.train/validate/${PROTOCOL}.development/apply/[0-9][0-9][0-9][0-9]/${PROTOCOL}.test.eval" ]; then
                echo "Submitting test n° $var"
                #qsub -j y -o loo_tst_${PROTOCOL}_${alpha//.}.txt -l mem_free=64G -l ram_free=64G -l gpu=1 -l num_proc=2 apply.sh $EXPERIMENT_DIR/train/${PROTOCOL}.train/validate/${PROTOCOL}.development $PROTOCOL
                #./apply.sh $EXPERIMENT_DIR/train/${PROTOCOL}.train/validate/${PROTOCOL}.development $PROTOCOL
                #sleep 2
            fi
        fi
        var=$((var+1))
	done
done
