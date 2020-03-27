#!/bin/bash

generate_system_list () {
    SYSTEM=$1
    echo "Creating Id-List for system '$SYSTEM'"
    LIST_FILE=ID_LIST_${SYSTEM}_2.txt
    touch $LIST_FILE && rm $LIST_FILE
    echo "#MISSION_SHORT;$SYSTEM" > $LIST_FILE
    for mission in $(ls ./missions)
    do
        echo ""
        short_name="${mission%_general.html}"
        echo "Scanning missions/$mission"
        sed -n '/<table.*>/I,/<\/table>/I{ /table>/Id; p}' ./missions/$mission | \
        sed -n '/<tr>/I,/<\/tr>/I{ s/^ *//g; s/^\t*//; s/^ *//g; p }' | \
        tr '[:lower:]' '[:upper:]' | \
        awk 'BEGIN{RS="<TR>"}NF>1{print "<TR>" substr(gensub(/\n/,"","g"),0,length($0))}' | \
        sed '/'$SYSTEM'/!d' | \
        sed -e 's/<TD WIDTH=".*"/<TD/g' -e 's/<TD BGCOLOR=".*"/<TD/g' \
            -e 's/<TD >/<TD>/g' -e 's/<TR>//g' -e 's/<\/TR>//g' \
            -e 's/<\/TD><TD>/\n/g' -e 's/<T[DR]>//g' -e 's/<\/T[DR]>//' \
            -e 's/ $//g' -e 's/<!--/\n<!--/g' | \
        awk '/^[[:digit:].]+$/{ print $0}' > TMP_LIST.txt
        n=$(cat TMP_LIST.txt | wc -l)
        cat TMP_LIST.txt | paste -sd "\n" > TMP_LIST2.txt
        cat TMP_LIST2.txt
        mv TMP_LIST2.txt TMP_LIST.txt
        #cat TMP_LIST.txt | paste -sd "," - > TMP_LIST.txt
        for pk in $(cat TMP_LIST.txt)
        do 
            echo "$short_name;$pk" >> $LIST_FILE
        done
        if [ $n -eq 0 ] ; then
            echo "$short_name;UNKNOWN" >> $LIST_FILE
        fi
        echo "$SYSTEM: $mission: $n"
        rm TMP_LIST.txt
    done
}

generate_system_list "NORAD"
generate_system_list "COSPAR"
generate_system_list "SIC"

