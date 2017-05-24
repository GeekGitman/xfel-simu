cd outfiles_mis/
echo -n '' > spimis.csv
for i in `seq 0 2000`;
do 
    if [ -f "ave_log_$i.txt" ] ; then
        echo -n $i, >> spimis.csv
        cat "ave_log_$i.txt" | grep -v time >> spimis.csv
    fi
done
mv spimis.csv ../

