#!/bin/bash

OgleTable=$1
## TODO: find RA/DEC data from Persson (2004) and incorporate
#PerssonTable=$2

awk '
  BEGIN {
    OFS="\t"
  }
  NR>1 {
    # ID,RA,DEC
    print $1,$5,$6
  }' $OgleTable
