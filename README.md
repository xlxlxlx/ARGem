# About ARGem

ARGem is a pipeline specialized for ARG analysis and is completely developed from the initial DNA short reads to the final visualization of results. It was designed for modest numbers of samples processed in one day and for affordable computational components, though the throughput could be easily increased through cloud resources. One feature of the ARGem pipeline is the essential use of project metadata provided by project creators to enable analysis of data across samples and projects. 

ARGem was built by research groups from Virginia Tech. This project is funded by USDA, grant number 2017-68003-26498.


# Prequisite
 - NCBI SRA toolkit: https://hpc.nih.gov/apps/sratoolkit.html
 - Python 3.X
 - MySQL >= 15.1
 - DIAMOND >= 0.9.12
 - BLAST >= 2.9.0

## Python libraries
 - luigi >= 3.0
 - pandas >= 0.25
 - numpy >= 1.17
 - PyMySQL >= 0.9
 - xlrd >= 1.2.0

# Usage

## Files and folders
- driver_retrieval:     folder w/ SRA retrieval driver
- driver_readmatching:  folder w/ short read matching driver
- driver_annotation:    folder w/ annotation driver
- driver_assembly:      folder w/ assembly driver
- driver_analysis:      folder w/ analysis driver
- userprojects:         projects (run w/ runscheduler.sh) stored here
- README.txt:           this file
- runscheduler.sh:      script to run the scheduler
- scheduler.py:         scheduler script

## Run the pipeline
- to run: ./runscheduler.sh <metadata file> <project ID> <user ID> <MGE database>
  - (example)  ./runscheduler.sh sample_metadata_upload_2.xlsx myProject myUser metacompare
- pipeline will either start immediately (if no other projects in the queue) or be added to the queue
- once pipeline is done running, find the project under /userprojects/


# Reference database
 - CARD: https://card.mcmaster.ca (version 3.1.0)
 - MobileOG: https://github.com/clb21565/mobileOG-db (version 01/22/2022)
 - MetaCompare: doi.org/10.1093/femsec/fiy079 (version 11/06/2018)
 - Parnanen et al. MGE Database: https://doi.org/10.1038/s41467-018-06393-w (version 08/16/2021)

The reference databases can be updated by the user to the current version.

# Acknowledge
The short read matching annotation tool is contributed by Suraj Gupta.   
CARD_classification_id.csv for co-occurrence network analysis is obtained from [CARD (Comprehensive Antibiotic Resistance Database)](https://card.mcmaster.ca/) and can be updated by the user to the current version.
