#!/usr/bin/awk -f
$1 = ((10 ^ ($1/5 + 1)) / 1000)
