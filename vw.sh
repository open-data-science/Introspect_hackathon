#!/bin/bash

FILENAME_TRAIN=$1
FILENAME_TEST=$2
LR=$3
NGRAMS=$4
# LINES=`wc -l ${FILENAME}`
# POS=`expr "${LINES}" : '.* '`
# COUNT_OF_LINES=${LINES:0:${POS}}
# COUNT_OF_LINES=$((COUNT_OF_LINES * 85 / 100))
# echo $COUNT_OF_LINES

# POS=`expr "${FILENAME}" : '.*\.'`
# NAME=${FILENAME:0:${POS} - 1}
# echo $NAME

#gshuf ${FILENAME} >> split -l $COUNT_OF_LINES
#mv xaa ${NAME}_train.vw
#mv xab ${NAME}_test.vw

gshuf ${FILENAME_TRAIN} -o ${FILENAME_TRAIN}

cd ../vowpal_wabbit/vowpalwabbit/
./vw -c -k -b 25 --oaa 12 -l ${LR} --ngram ${NGRAMS} -d ../../Introspect_hackathon/${FILENAME_TRAIN} -f vw_ods_channels.bin --passes 20 --holdout_off
./vw -t -i vw_ods_channels.bin -d ../../Introspect_hackathon/${FILENAME_TEST}

# predict
./vw -t -i vw_ods_channels.bin -d ../../Introspect_hackathon/${FILENAME_TEST} -p ../../Introspect_hackathon/${FILENAME_TEST}.pred --quiet

mv vw_ods_channels.bin ../../Introspect_hackathon/models/