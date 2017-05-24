mkdir h5files
mkdir backup
mv p*/lstc*.h5 ./h5files
mv p0 ./backup/backup_p0
mv p1 ./backup/backup_p1
mv p3 ./backup/backup_p3
mv p111 ./backup/backup_p111
nohup rm -rf ./p* &
