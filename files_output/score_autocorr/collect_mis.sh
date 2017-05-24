cd corrlog_mis/
echo -n '' > ac_mis.csv
for i in `seq 0 2000`;
do 
    if [ -f "ave_corr$i.txt" ] ; then
        echo -n $i, >> ac_mis.csv
        cat "ave_corr$i.txt" | grep -v time >> ac_mis.csv
    fi
done
mv ac_mis.csv ../

