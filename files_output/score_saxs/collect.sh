cd outfiles_saxs/
echo -n '' >> saxs.csv
for i in `seq 0 2000`;
do 
    if [ -f "g3_0_lstc$i.txt" ] ; then
        echo -n $i, >> saxs.csv
        cat "g3_0_lstc$i.txt" | grep -v time >> saxs.csv
    fi
done
mv saxs.csv ../

