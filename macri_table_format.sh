#!/usr/bin/bash

MacriTable3=$1
MacriTable5=$2

# format lines from Macri14_Table_3
awk '
  BEGIN {
    OFS="\t"
  }
  NR>38 {
    print "OGLE-LMC-CEP-"$1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$15,$17
  }' $MacriTable3

# format lines from Macri14_Table_5
sed 's/OGL-/OGLE-LMC-CEP-/' $MacriTable5 \
  | awk '
      BEGIN {
        OFS="\t"
      }
      NR>42 {
        print $1,$2,"FU",$3,$4,$5,$6,$7,$8,$9,$10,$11,$12
    }'
