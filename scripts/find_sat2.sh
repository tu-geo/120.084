#!/bin/bash

MISSIONS_DIR="../data/missions"

generate_system_list () {
    SYSTEM=$1

    # echo "Creating Id-List for system '$SYSTEM'"
    LIST_FILE=ID_LIST_${SYSTEM}.txt
    #touch $LIST_FILE && rm $LIST_FILE
    echo "#mission;NORAD;COSPAR;HASH" > $LIST_FILE
    for mission in $(ls $MISSIONS_DIR)
    do
        # echo ""
        short_name="${mission%_general.html}"
        # echo "Scanning missions/$mission"
        # Remove everything except the table
        sed -n '/<table.*>/I,/<\/table>/I{ /table>/Id; p}' $MISSIONS_DIR/$mission | \
        # Get all the rows
        sed -n '/<tr>/I,/<\/tr>/I{ s/^ *//g; s/^\t*//; s/\n//g; s/^ *//g; s/ //g; p }' | \
        # Change case
        tr '[:lower:]' '[:upper:]' | \
        # Clean tags
        awk 'BEGIN{RS="<TR>"} NF>1 {print "<TR>" substr(gensub(/\n/,"","g"),0,length($0))}' | \

        sed -e 's/<TD WIDTH=".*"/<TD/g' \
            -e 's/BGCOLOR="#......"//g' \
            -e 's/WIDTH=".*"//g' \
            -e 's/  //g' \
            -e 's/<TR>//g' \
            -e 's/<\/TR>//g' \
            -e 's/<!--/\n<!--/g' > TMP_LIST.txt

        # cat TMP_LIST.txt
        # echo " BREAK "
        # ^<TR><TD>.*NORAD[\dA-Z\:\(\)]*<\/TD>((<TD>\d{1,5}<\/TD>)+)<\/TR>
        # sed 's/^<TR>.*NORAD[0-9A-Za-z:()]*<\/TD>\(\(<TD>[0-9]\{1,5\}<\/TD>\)\+\)<\/TR>/\2/g' TMP_LIST.txt > TMP_LIST2.txt
        sed -n '/NORAD/p' TMP_LIST.txt > TMP_LIST_NORAD.txt
        sed -n '/COSPAR/p' TMP_LIST.txt > TMP_LIST_COSPAR.txt
        # <TR><TD>.*NORAD.*:</TD>(<TD>.*</TD>)+
        # cat TMP_LIST_NORAD.txt
        # cat TMP_LIST_COSPAR.txt

        python3 python_helper.py TMP_LIST_NORAD.txt TMP_LIST_COSPAR.txt $mission >> $LIST_FILE
        rm TMP_LIST_COSPAR.txt TMP_LIST_NORAD.txt TMP_LIST.txt

    done
    cat $LIST_FILE
}

generate_system_list "ALL"

