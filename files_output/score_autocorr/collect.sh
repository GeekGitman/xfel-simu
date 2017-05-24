cd outfiles_ac/
echo -n '' > ac.csv
for i in `seq 0 2000`;
do 
    if [ -f "ave_log_$i.txt" ] ; then
        echo -n $i, >> ac.csv
        cat "ave_log_$i.txt" | grep -v time >> ac.csv
    fi
done
mv ac.csv ../

