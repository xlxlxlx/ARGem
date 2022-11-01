# Buffer Line
import re
import os
import sys
import time
import datetime
import subprocess
import json


class MegaHitDriver:
    '''
    Class responsible for running the MEGAHIT Assembler.
    '''
    def __init__(self, proj_path):

        # this is the project folder the results are outputted
        self.proj_path = proj_path

        self.megahit_path = ""
        self.SRA_path = "sra_data"

    def run_megahit(self):
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
                print(error_message)
                print(file_one, file_two)
                error_count += 1
                self.error_log(key, error_message)

            # Directory correctly contains two fasta files for annotation
            else:
                output_dir = f"{self.proj_path}/assembly_output/{key}_assembled"
                print(f"mkdir -p {self.proj_path}/assembly_output")
                subprocess.run(f"mkdir -p {self.proj_path}/assembly_output", shell=True)

                # call MEGAHIT to assemble the contigs
                print(f"{self.megahit_path}/megahit -1 {file_one} -2 {file_two} -o {output_dir}")
                subprocess.run(f"{self.megahit_path}/megahit -1 {file_one} -2 {file_two} -o {output_dir}", shell=True)

        # write to outcome.json
        with open(f"{self.proj_path}/outcome.json", "r+") as outcome_file:
            data = json.load(outcome_file)
            # case 1: no errors
            if error_count == 0:
                data['assembly_outcome'] = 'Success'
            # case 2: some errors, some successes
            elif error_count < len(sra_num_list):
                data['assembly_outcome'] = 'Success*'
            # case 3: all errors
            else:
                data['assembly_outcome'] = 'Failure'
            outcome_file.seek(0)
            json.dump(data, outcome_file, indent=4)
            outcome_file.truncate()


    def error_log(self, sra_value, error_message):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MegaHit-Error-Log.tsv"), "a+", encoding='utf-8') as file_ptr:
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
    megahitDvr = MegaHitDriver(proj_path)
    megahitDvr.run_megahit()

    print(f"[Total Time Spent: {round((time.time() - ini_time), 2)} seconds]")
