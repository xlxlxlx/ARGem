# About ARGem

ARGem is a pipeline specialized for ARG analysis and is completely developed from the initial DNA short reads to the final visualization of results. It was designed for modest numbers of samples processed in one day and for affordable computational components, though the throughput could be easily increased through cloud resources. One feature of the ARGem pipeline is the essential use of project metadata provided by project creators to enable analysis of data across samples and projects. 

ARGem was built by research groups from Virginia Tech. This project is funded by USDA, grant number 2017-68003-26498.

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

## Running the pipeline
- to run: ./runscheduler.sh <metadata file> <project ID> <user ID> <MGE database>
  - (example)  ./runscheduler.sh sample_metadata_upload_2.xlsx myProject myUser metacompare
- pipeline will either start immediately (if no other projects in the queue) or be added to the queue
- once pipeline is done running, find the project under /userprojects/
