# xstruct
 doi:  10.3389/fmolb.2017.00023



## Main Step：
- Run ZDOCK to  generate protein complexes
- Generate scattering patterns (Using C++ version)
- Score calculation and visualization (Choose one score to calculate and analysis)


## **Folder Structure**
```none
Demo
	├── ZDOCK             #make predictions
	│   ├── benchmark5    #ZDOCK benchmark
	│   └── zdock3.0.2_linux_x64      #ZDOCK program
	├── files_pdb		  #All predicted complexes
	├── job.py    		  #Submit the job to the server
	├── root			  #Generate patterns
	└── files_output      #For data analysis
	    ├── h5files	      #HDF5 files (patterns for orientation matching)
  	    ├── h5grid3	      #HDF5 files (patterns on grid for orientation mismatching)
   	    ├── h5rand	      #HDF5 files (patterns randomly distributed for orientation mismatching)
   	    ├── score_autocorr #calculate and compare autocorrelation 
   	    ├── score_spi     #calculate and compare SPI score 
   	    └── score_saxs    #calculate and compare SAXS score 
```

# ZDOCK
**Task**：Generate 2000 predicted complexes with Receptor and Ligand
**Path** : Demo/ZDOCK
**Input**：`receptor.pdb`
**Output**：`Demo/files_pdb/c*.pdb`

**How to run**:
```bash
	cd ZDOCK
	#zdock3.0.2_linux_x64 and benchmark are already downloaded from https://zlab.umassmed.edu
	#wget https://zlab.umassmed.edu/benchmark/benchmark5.tgz #zdock benchmark
	cd zdock3.0.2_linux_x64
	cp ../benchmark5/structures/1E6J_*_b.pdb . # You may change '1E6J' to one other protein
	#please refer to ../benchmark5/README.
	#*_b.pdb means bound docking.

	#Run zdock to generate complex, please refer to ZDOCK/README
	mark_sur 1E6J_r_b.pdb receptor_m.pdb
	mark_sur 1E6J_l_b.pdb ligand_m.pdb
	#reconstruct native structure c0.pdb
	cat receptor_m.pdb > c0.pdb
	cat ligand_m.pdb >> c0.pdb
	#use ZDOCK to predict structures
	zdock -R receptor_m.pdb -L ligand_m.pdb -o zdock.out
	create.pl zdock.out

	#Rename the complexes
	mkdir files_pdb
	mv complex*.pdb ./files_pdb/ && mv c0.pdb ./files_pdb/ && cd files_pdb
	for v in `seq 2000`; do
	    mv "complex.$v.pdb" "c$v.pdb"
	done
	#move the output to root dict
	mv ./files_pdb/ Demo/files_pdb

	#(Optional)To combine all the complexes in one file, run following code:
	for i in `seq 0  2000`
	do
		cat c$i.pdb >> "all.pdb"
	    echo "ENDMDL" >> "all.pdb"
	done	
```
Before generating the patterns, you **MUST** _align_ the complexes! (Using VMD.)

# Pattern Generation:

#### **Input:** 
 * Atom coordinates: `Demo/files_pdb/c*.pdb`
 * Experimental parameters (wave length, screen size, pixel size, pixel number): in `./root/task.input` 
	
#### **Output:**
  * scattering patterns in `Demo/file_output/h5files/*.h5`

*Note:* Use `h5ls` or `h5dump` in linux shell to browse the HDF5 files.

#### **Folder Structure**
```none
Demo/root/
	├── qsubbatch.pbs     #summit the job (./run.sh) to the server
	├── qsublow.pbs
	├── run.sh            #../job.py call this script to generate patterns.
	├── task.input        #parameters. You should modify all the parameters here
	├── init.py           #initialize the parameters and generate "parameters.cpp" and "task"
	├── main.cpp          #main function
	├── model.cpp         #functions to read, rotate the protein and generate the patterns
	├── vec3.cpp          #functions for 3D matrix calculation
	├── parameter.cpp     #Automatically generated function. Do NOT manually modify it.
	├── s/                #Temporary files
	└── fitangle.py       #collect patterns from the ./s/ and generate HDF5 file
```

#### **Step:**
1. All the parameters can be set in `./root/task.input`. 
2. Then the `Demo/job.py` call `Demo/root/run.sh`
3. `init.py` read `task.input`, and automatically generate `parameter.cpp` and `task`.
4. The main function generate patterns in `Demo/root/s/PROTEIN_NAME:COMPLEX_NUM:angle1,angle2,angle3.dat`(e.g. `c0:0:0,0,0.dat` )
5. `fitangle.py` collect the files in `Demo/root/s/`, and save the patterns and angles in `lstPROTEIN_NAME.h5`(e.g. lstc1.h5)

*Note: * `lstc0.h5` is the patterns of the native structure (RMSD=$0\mathring{A}$).   `lstcN.h5` are the patterns of predict structures.

	
#### **How to run:**
```bash
	cd demo
	cp -r ./ZDOCK/zdock3.0.2_linux_x64/files_pdb .       #all the complexes files
	vim ./root/task.input            #set the experimental parameters
	vim job.py                       #set the running parameters
	python job.py                    #submit to the server
	#----------You may wait for days...————————————————————
	#Note: before you run ./clean.sh, please make sure that ./pn/lstcn.h5 files are correctly generated
	./clean.sh                       #collect the result file 
	mv h5files/ files_output/
```

+ **set the experimental parameters**
The key parameters: screen pixel number, distance to screen, wave length, etc... can be modified in `Demo/root/task.input`.

	Switch `RAND_EULER=ON` will generate `rand_euler_num` orientations which randomly distributed on sphere.
You could manually set orientations by appending `angle=ANG1,ANG2,ANG3` to this file.


+ **set the running parameters**
Run `Demo/job.py` to submit the task to the server.  `nlst1` is the complex list. (e.g. if nlst1=[0,1,2], the program will calculate the patterns for `c0.pdb` (the native structure), `c1.pdb` (the predicted structure of the highest score of ZDOCK) and `c2.pdb`.)

	*Note: *
1. In `job.py`, the line: `sed -i \'2c protein_file='+pdbname+'\' task.input` will automatically modify the second line in `task.input`, making the protein name same as you assigned (parameter`nlst1` in `job.py`). 
2. To summit the jobs to the other queue, you should modify the `root/qsublow.pbs`


#### Generate grid in (-22.5°, 22.5°)   (Optional, only for oritentaion mismatching case)
The program will generate a set of angles on grid, like [(-22.5,-22.5,-22.5),(-22.5,-19.5,-22.5),(-22.5,-16.5,-22.5)...(22.5,22.5,22.5)]; and a set of random angles within the range, like[(-15.3, 21.9 ,5.2),(10.7, -3.0, 17.9), (-4.0, 0.1, -9.6), ... ] .

```bash
    cd  gen_grid
    #modify the grid mesh here
    vim gen_grid.py
    python gen_grid.py
    #paste the output as the input (angles of grid mesh)
    cat taskgrid.txt >> Demo/root/task.input
    #Or (random angles):
    cat taskrand.txt >> Demo/root/task.input
```

#### Add noise (Optional)
The following code generate patterns with Poission and Gaussian noise. Output files would be saved in `Demo/review/noise/h5noise`
```bash
	cd Demo/review/noise
	ln -s Demo/files_output/h5files .
	vim addnoise.py #set SNR of Gaussian noise in this file.
	python addnoise.py
```	


# Score calculation I - **(orientation match)**
#### **Input:** 
*  scattering patterns in `./files_output/h5files/*.h5`
	
#### **Output:**
*  SPI score:  `./files_output/score_spi/spi.csv`
*  Auto correlation score:  `./files_output/score_autocorr/autocorr.csv`
*  SAXS score:  `./files_output/score_saxs/saxs.csv`

#### **Folder structure:**
 
### SPI score
#### **How to run:**
```bash
	cd Demo/files_output/score_spi

	#Serial Mode:
	python compare_spi.py
	#Or Parallel Mode:
	python compare_spi.py N  #N is the number of threads.  
	
	python compare_spi_collect_result.py
```
Then `spi.csv` is generated. The first column is the complex index, the second column is the spi score.

### Auto-correlation score
Lanqing Huang made contribution to the program.
#### **How to run:**
```bash
	cd Demo/files_output/score_ac
	
	#serial Mode
	python calc_ac.py          #calculate the auto-correlation, the auto-coreelation files are stored in files_output/score_ac/autocorr
	#Parallel Mode
	python calc_ac.py N        #N is the number of threads.
	
	python compare_ac.py 
	python compare_ac_collect_result.py
```
Then `ac.csv` is generated. The first column is the complex index, the second column is the auto correlation score.

### SAXS score

#### **How to run:**
```bash
	cd Demo/files_output/score_saxs
	python calc_saxs.py          #calculate the auto-correlation 
	python compare_saxs.py 
	python compare_saxs_collect_result.py
```
Then `SAXS.csv` is generated. The first column is the complex index, the second column is the saxs score.

# Score calculation II - **(orientation mismatching)**
#### **Input:** 
*  scattering patterns in `./files_output/h5gridN/*.h5` N=2,3,5,9 for _grid step_ = $2^\circ,3^\circ,5^\circ,9^\circ$ 

*Note:* The scattering pattern generation steps are same as the steps of orientation matching.  You should manually modify the orientations in `./root/task.input` or type `cat task.input.gridN >> task.input`.
 After you modify, the `task.input` should be like `task.input.examplegrid3`
	
#### **Output:**
*  SPI score:  `./files_output/score_spi/spimis.csv`
*  Auto correlation score:  `./files_output/score_autocorr/autocorrmis.csv`
*  SAXS score:  `./files_output/score_saxs/saxsmis.csv`

#### **Folder structure:**
 
### SPI score
#### **How to run:**
Same as orientation matching case, except the Path.
```bash
    	cd files_output/score_mis_spi
    	#Serial Mode:
	python compare_spi_mis.py
	#Or Parallel Mode:
	python compare_spi_mis.py N  #N is the number of threads.  
	#change the output path in this file
	vim compare_spi_collect_result.py 
	python compare_spi_collect_result.py
```

### Auto correlation
#### **How to run:**
```bash
	cd Demo/files_output/score_ac

	#serial Mode
	python calc_ac_mis.py          #calculate the auto-correlation, the auto-coreelation files are stored in files_output/score_ac/autocorr
	#Parallel Mode
	python calc_ac_mis.py N        #N is the number of threads.
	
	python compare_ac_mis.py 
	python compare_ac_collect_result_mis.py
```
### SAXS score

#### **How to run:**
```bash
	cd Demo/files_output/score_saxs
	python calc_saxs_mis.py          #calculate the auto-correlation 
	python compare_saxs_mis.py 
	python compare_saxs_collect_result_mis.py
```


# Score calculation III - Visualization

### Scattering plot, Probability curve, and AUC area

**Before you plot, you need to calculate _RMSD_ first. Then save the `rmsdN.csv` in folder `scatterplot/`**
Then you need to save the output of the score(SPI/Autocorr/SAXS) file (`spiN.csv`/`acN.csv`/`saxsN.csv`) in the folder `./hybN/`
After you run the following code, the images would be saved in `./graph/N/`
```bash
    cd Demo/review/scatterplot
    cp Demo/files_output/score_spi/spi.csv . # Or you can plot autocorr, saxs etc.. As long as the first column is index, second column is score
    cp Demo/rmsd.csv .#You need to calculate RMSD using VMD
    python plot.py
```	
*Note:* You need to modify the last few lines of the program for different input data. Please read the comments in the `plot.py`.

### Histogram (orientation mismatching)
Histogram figure is the visualization of orientation mismatching. Before you run, you need to copy or link the output files of the `./files_output/score_mis_autocorr/`
```bash
	cd Demo/review/hist
	ln -s Demo/files_output/score_mis_spi/output_mis .
	#make the figures of the histogram
	python hist.py
	#calculate the mean bias and standard division of the orientation mismatching
	python stats.py
```	







# Classification for every single patterns


### Joint Training
**Input:** `zdockjointfilenames_table.csv`, which contains all the path to the SPI score, Auto correlation and SAXS score.
**Format:** 
		PathSPI1,PathAutocorr1,PathSAXS1
		PathSPI2,PathAutocorr2,PathSAXS2
		...
		...
**Output:** ROC curve and AUC value. 
**Parameters** You can modify the type of classifier(kNN(*Recommended*), Regression, and SVM) , ratio of test and training dataset in the `zdockjointanalysis.py`


This program aims to classifyr all the 3 parameters (SPI score, Auto correlation, SAXS score) to cla
```bash
	#You need to modify the Path to your SPI.csv, AutoCorr.csv, SAXS.csv in this file.
	vim zdockjointfilenames_table.csv
	python ./zdockjointanalysis.py zdockjointfilenames_table.csv 
```


# Other 

### generate patterns with python (Much slower than  C++)
This program read the parameters from `task.input` (should be in same path) , generate patterns and save in HDF5 format. The code is much clear than the C++ version.
```bash
cd other/GenPattpy
vim 1patt.py
python 1patt.py
```

### calculate  and compare the intensity in 3D space(python)
This program calcuate the intensities in 3D reciprocal space. You can use Xuanxuan Li's dataviewer to visualize the result.
```bash
cd other/3D
python gen3D.py
```


