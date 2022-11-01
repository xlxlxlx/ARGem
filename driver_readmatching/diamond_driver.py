# Buffer Line
import re
import os
import sys
import time
import datetime
import subprocess
import json


class DiamondDriver:
    '''
    Class responsible for running the Short Reads Matching.
    '''
    def __init__(self, proj_path):

        # this is the project folder the results are outputted
        self.proj_path = proj_path

        self.pipeline_path = "diamond-annotation/"
        self.SRA_path = "sra_data"

    def run_diamond(self):
        print("Step: short reads matching")
                      
        sra_num_list = []
        
        
        with open(os.path.join(self.proj_path, 'SRA_list'), "r", encoding="utf-8") as sra_list_file:
            lines = sra_list_file.readlines()
            sra_num_list = lines[0].split(',')[:-1]
        print(sra_num_list)

        error_count = 0
        for key in sra_num_list:
            key = key.strip()
            file_one = f"{self.SRA_path}/{key}/{key}_1.fastq"
            file_two = f"{self.SRA_path}/{key}/{key}_2.fastq"
            
            # Only 1 or less fasta file is present in the directory -> throws error
            if not os.path.exists(file_one) or not os.path.exists(file_two):
                error_message = "Error: no enought fastq files available for assembly."
                error_count += 1
                self.error_log(key, error_message)

            # Directory correctly contains two fasta files for annotation
            else:
                output_dir = f"/agroseek/www/wp-includes/task_scheduler/{self.proj_path}/shortreads_output"
                subprocess.run(f"mkdir -p {self.proj_path}/shortreads_output", shell=True)

                # call diamond pipeline to generate normalized annotations

                # where to look for the results...
                fileOutput = f"{output_dir}/{key}.shortreads.csv"
                fileOutputFinal = f"{output_dir}/{key}.shortreads.csv.clean.card.matches.quant.normalization"#os.chdir(f'{self.pipeline_path}')
                subprocess.run(f"python3 {self.pipeline_path}/diamond_pipeline.py --forward_pe_file {file_one} --reverse_pe_file {file_two} --output_file {output_dir}/{key}.shortreads.csv --database card", shell=True)
                print(f"python3 {self.pipeline_path}/diamond_pipeline.py --forward_pe_file {file_one} --reverse_pe_file {file_two} --output_file {output_dir}/{key}.shortreads.csv --database card")
                #os.chdir('../')


    def error_log(self, sra_value, error_message):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ShortReads-Error-Log.tsv"), "a+", encoding='utf-8') as file_ptr:
            labels = "Error Time\tSRA Number\tError\n"
            file_ptr.seek(0)
            first_line = file_ptr.readline()
            if first_line != labels:
                file_ptr.write(labels)

            error_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file_ptr.write(f"{error_time}\t{sra_value}\tError: {error_message}.\n")

# Driver Code
if __name__ =="__main__":
    ini_time = time.time()

    proj_path = sys.argv[1]  # 1st argument should be project name
    diamondDvr = DiamondDriver(proj_path)
    print("Step: running driver")
    diamondDvr.run_diamond()

    print(f"[Total Time Spent: {round((time.time() - ini_time), 2)} seconds]")

