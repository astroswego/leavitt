#!/usr/bin/awk -f
{
    # initialize average
    avg = 0;
    # sum over the rows
    for (i=1; i<=NF; i++)
        avg += $i;
    # divide by number of fields
    avg /= NF;
    # print the average
    print avg;
}
