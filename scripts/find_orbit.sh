#!/bin/bash

NORAD_FILE=20200312-active_satellites.txt

for mission in $(cat ID_LIST_NORAD.txt)
do
    name=$(echo $mission | cut -d";" -f 1)
    if [ "x$name" = "x#MISSION_SHORT" ] ; then
        continue
    fi
    norads=$(echo $mission | cut -d";" -f 2)

    echo ""
    echo "-----------------------------------------"
    echo "Processing mission $name"
    echo "Found norad-ids: $norads"
    for norad in $(echo $norads | sed -e 's/,/ /g') ; do
        echo ""
        echo "Name: $name, Number: $norad"
        if [ "x$norad" = "xUNKNOWN" ] ; then
            echo "---------------------------------cannot process $name"
            continue
        fi
        nf=$(echo $norad | awk '{printf("%05d", $1)}')
        #echo "process $nf"
        sed -e '/^[12] '$nf'.*/!d' $NORAD_FILE
    done
done

