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
    Class responsible for running the MEGAHIT Assembler. (Kevin)
    '''
    def __init__(self, proj_path):

        # this is the project folder the results are outputted
        self.proj_path = proj_path

        self.megahit_path = "../../../assembly_tools/MEGAHIT-1.2.9-Linux-x86_64-static/bin/"
        self.SRA_path = f"{proj_path}/raw_sequence_data"

    def run_megahit(self):
        sra_table = {}
        sra_num_list = []
        result = subprocess.getoutput(f'find {self.SRA_path}/SRR*')
        result = result.split('\n')

        # Find all SRA accession numbers in the designated directory
        for sra_folder in result:
            sra_folder = sra_folder.replace(f'{proj_path}/raw_sequence_data/', '')

            if re.search("SRR[0-9]+$", sra_folder, re.IGNORECASE) != None:
                sra_num_list.append(sra_folder)

        # Determines if the directories for each SRA number contain the correct number of fasta files
        print(sra_num_list)
        for sra_num in sra_num_list:
            for sra_folder in result:
                if re.search(f"{sra_num}_1.fastq", sra_folder) != None:
                    sra_table[sra_num] = 2
                    break
                else:
                    sra_table[sra_num] = 1

        error_count = 0
        for key in sra_table:
            value = sra_table[key]

            # Only 1 or less fasta file is present in the directory -> throws error
            if value == 1:
                error_message = "Error: Only one fastq file is available for assembly."
                error_count += 1
                self.error_log(key, error_message)

            # Directory correctly contains two fasta files for annotation
            elif value == 2:
                file_one = f"{self.SRA_path}/{key}/{key}_1.fastq"
                file_two = f"{self.SRA_path}/{key}/{key}_2.fastq"
                output_dir = f"{self.proj_path}/assembly_output/{key}_assembled"
                subprocess.run(f"mkdir -p {self.proj_path}/assembly_output", shell=True)

                # call MEGAHIT to assemble the contigs
                subprocess.run(f"{self.megahit_path}/megahit -1 {file_one} -2 {file_two} -o {output_dir}", shell=True)

        # write to outcome.json
        with open(f"{self.proj_path}/outcome.json", "r+") as outcome_file:
            data = json.load(outcome_file)
            # case 1: no errors
            if error_count == 0:
                data['assembly_outcome'] = 'Success'
            # case 2: some errors, some successes
            elif error_count < len(sra_table):
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
