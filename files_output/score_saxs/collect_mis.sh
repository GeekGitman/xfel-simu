cd outfiles_saxs_mis/
echo -n '' > saxs_mis.csv
for i in `seq 0 2000`;
do 
    if [ -f "ave_lstc$i.txt" ] ; then
        echo -n $i, >> saxs_mis.csv
        cat "ave_lstc$i.txt" | grep -v time >> saxs_mis.csv
    fi
done
mv saxs_mis.csv ../

