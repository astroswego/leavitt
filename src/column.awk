{
    # print magnitude
    printf $(i+3) "\t";
    # print leading 0's in shared terms
    for (col = 0; col < 2 * i; col++)
        printf "0\t";
    # print logP and constant term
    printf $2 "\t1\t";
    # print trailing 0's in shared terms
    for (col = 2 * (i + 1); col < 2 * n; col++)
        printf "0\t";
    # print leading 0's in individual terms
    for (col = 1; col < NR; col++)
        printf "0\t";
    # print individual's constant
    printf "1";
    for (col = NR; col < lines; col++)
        printf "\t0";
    printf "\n";
}
