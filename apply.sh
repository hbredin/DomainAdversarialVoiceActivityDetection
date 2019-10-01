#!/bin/bash
#$ -cwd
#$ -V
#$ -l 'gpu=1,mem_free=32g,ram_free=32g,hostname=b1[12345678]*|c*'
#$ -l num_proc=2
#$ -q *.q

# this script is called like "./apply2.sh $PATH_TO_DEV_FOLDER $PROTOCOL_TEST
export CUDA_VISIBLE_DEVICES=`free-gpu`

# Get arguments
DEV_FOLDER=$1
PROTOCOL_TEST=$2

source activate pyannote
pyannote-speech-detection apply --gpu $DEV_FOLDER $PROTOCOL_TEST

