# About ARGem

ARGem is a pipeline specialized for ARG analysis and is completely developed from the initial DNA short reads to the final visualization of results. It was designed for modest numbers of samples processed in one day and for affordable computational components, though the throughput could be easily increased through cloud resources. One feature of the ARGem pipeline is the essential use of project metadata provided by project creators to enable analysis of data across samples and projects. 

ARGem was built by research groups from Virginia Tech. This project is funded by USDA, grant number 2017-68003-26498.


# Prequisite
 - NCBI SRA toolkit: https://hpc.nih.gov/apps/sratoolkit.html
 - Python 3: https://www.python.org/
 - MySQL >= 15.1: https://www.mysql.com/
 - DIAMOND >= 0.9.12: https://github.com/bbuchfink/diamond
 - BLAST >= 2.9.0: https://blast.ncbi.nlm.nih.gov/doc/blast-help/downloadblastdata.html

## Python libraries
 - luigi >= 3.0
 - pandas >= 0.25
 - numpy >= 1.17
 - PyMySQL >= 0.9
 - xlrd >= 1.2.0

# Usage

## Install the pipeline
- Download the entire directory of the pipeline
- Install dependencies in Python    
  Go to the pipeline's directory in terminal and type the following command:    
  `pip install -r requirements_w_versions.txt`    
- Install other listed prequisite (with URL links provided)
- Create MySQL tables for the pipeline using the following command:   
  `mysql -u username -p database_name < create_tables.sql`

## Run the pipeline
- To run the pipeline, go to the pipeline's directory in terminal and type the following command:    
  `./runscheduler.sh <metadata file> <project ID> <user ID> <MGE database>`    
Example command: 
  `./runscheduler.sh sample_metadata_upload_2.xlsx myProject myUser metacompare`
- The pipeline will either start immediately (if no other projects in the queue) or be added to the queue
- Once a project is done processing, find the project under /userprojects/. The results of each stage should be in their subdirectories.

# Optional configurations on the pipeline

Two databases can be added to the shortread matching step.
 - DeepARG (an ARG reference database): https://doi.org/10.1186/s40168-018-0401-z
 - GreenGenes (a 16S rRNA gene database): https://greengenes.secondgenome.com/
The database files can be put under:
 - driver_readmatching/diamond-annotation/bin/deeparg （for DeepARG database)
 - driver_readmatching/diamond-annotation/bin/gg13 （for GreenGenes database)

If the paths to the tools (SRA Toolkit, BLAST, and DIAMOND) need to be changed, change the corresponding variables in:
 - driver_retrieval/sra_retriever.py
 - driver_assembly/megahit_driver.py
 - driver_annotation/blast_driver.py
 - driver_annotation/diamond_driver.py
 - driver_annotation/annotation_driver.py

The configurations of the short read matching step can be changed according to the README in `driver_readmatching/diamond-annotation/`


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

# Reference database
 - CARD: https://card.mcmaster.ca (version 3.1.0)
 - MobileOG: https://github.com/clb21565/mobileOG-db (version 01/22/2022)
 - MetaCompare: doi.org/10.1093/femsec/fiy079 (version 11/06/2018)
 - Parnanen et al. MGE Database: https://doi.org/10.1038/s41467-018-06393-w (version 08/16/2021)

The reference databases can be updated by the user to the current version.

Once obtained, the reference database can be processed by DIAMON using a command like below:
<code>diamond makedb --in db_name.fasta -d db_name </code>

This will generate a `db_name.dmnd` file. The generated `.dmnd` files need to be put under:
 - driver_annotation/databases
 - driver_readmatching/diamond-annotation/bin/card （for CARD databae)




# Acknowledge
The short read matching annotation tool is contributed by Suraj Gupta.   

CARD_classification_id.csv for co-occurrence network analysis is obtained from [CARD (Comprehensive Antibiotic Resistance Database)](https://card.mcmaster.ca/) and can be updated by the user to the current version.
