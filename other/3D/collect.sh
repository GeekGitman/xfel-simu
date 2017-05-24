for i in 1 2 3 4 5 6 7 8 
do
    echo $i
    cd p$i
    #mkdir output
    #mv ./re*.h5 ./output/
    #mkdir files_pdb
    #mv *.pdb ./files_pdb/
    cp ../compare_3d.py . 
    python compare_3d.py > ../result/resultall.csv
    cd ..
done
