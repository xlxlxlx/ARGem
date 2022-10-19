'''
- can only be invoked within the scheduler.py script
  - invoked as: python3 driver_assembly/diamond_driver.py <project ID>
- after invocation, creates a subfolder under project folder called "annotations" containing output
'''

import sys
import subprocess
import csv
import re
import os
import json
from timeit import default_timer as timer

class DiamondDriver:
    def __init__(self, proj_path):

        # this is the project folder the results are outputted
        self.proj_path = proj_path

        # paths to important stuff
        self.diamond_path = ""
        self.blastn_path = ""
        self.card_dmnd_path = "driver_annotation/databases/card-3.1.2.dmnd"
        self.larsson_path = "driver_annotation/databases/larsson.fasta"
        self.metacompare_dmnd_path = "driver_annotation/databases/metacompare.dmnd"
        self.assembly_path = f"{proj_path}/assembly_output"


    def run_diamond(self):
        # for logging
        got_annotated = []  # SRR's that got annotated
        not_annotated = []  # SRR's that didn't get annotated (empty contig)

        print('running DIAMOND...')
        timestart = timer()

        # get assembly folder names (SRR[...]_assembled)
        # NOTE: THEY MUST ALL BE UNIQUE NAMES FOR NOW...
        assembly_folders = []
        result = subprocess.getoutput(f'find {self.assembly_path}/SRR*')
        result = result.split('\n')
        for assembly_folder in result:
            assembly_folder = assembly_folder.replace(f'{self.assembly_path}/', '')
            if re.search("SRR[0-9]+_assembled$", assembly_folder, re.IGNORECASE) != None:
                assembly_folders.append(assembly_folder)

        # make subdirectories for all assembled output, then
        # run diamond on card, larsson* and metacompare for all their final.contigs.fa
        # *larsson incompatible w/ diamond, must use blastn/tblastx
        print(assembly_folders)
        error_count = 0
        for assembly_folder in assembly_folders:
            assembly_folder_truncated = assembly_folder.replace('_assembled', '')
            # first check if current assembly's contig is empty
            if os.path.getsize(f'{self.assembly_path}/{assembly_folder}/final.contigs.fa') == 0:
                not_annotated.append(assembly_folder_truncated)
                error_count += 1
                continue

            subprocess.run(f'mkdir -p {self.proj_path}/annotations/{assembly_folder_truncated}_annotated', shell=True)
            out_path = f'{self.proj_path}/annotations/{assembly_folder_truncated}_annotated/'

            # run it!
            subprocess.run(f'{self.diamond_path}/diamond blastx -d {self.card_dmnd_path} --query {self.assembly_path}/{assembly_folder}/final.contigs.fa --out {out_path}/out_card.tsv --outfmt 6 --threads 64 --evalue 1e-10', shell=True)
            # subprocess.run(f'{self.blastn_path}/blastn -db {self.larsson_path} -query {to_annotate}/{contig} -out {out_path}/out_larsson.tsv -outfmt 6 -num_threads 64 -evalue 1e-10', shell=True)
            subprocess.run(f'{self.diamond_path}/diamond blastx -d {self.metacompare_dmnd_path} --query {self.assembly_path}/{assembly_folder}/final.contigs.fa --out {out_path}/out_metacompare.tsv --outfmt 6 --threads 64 --evalue 1e-10', shell=True)

            got_annotated.append(assembly_folder_truncated)

        timeend = timer()
        print(f'done running... that took {timeend - timestart} seconds')

        # write to outcome.json
        with open(f"{self.proj_path}/outcome.json", "r+") as outcome_file:
            data = json.load(outcome_file)
            # case 1: no errors
            if error_count == 0:
                data['annotation_outcome'] = 'Success'
            # case 2: some errors, some successes
            elif error_count < len(assembly_folders):
                data['annotation_outcome'] = 'Success*'
            # case 3: all errors
            else:
                data['annotation_outcome'] = 'Failure'
            outcome_file.seek(0)
            json.dump(data, outcome_file, indent=4)
            outcome_file.truncate()

        # write annotation results to log
        with open(f'{self.proj_path}/annotations/log.txt', 'a') as log:
            log.write("=== ANNOTATION RESULTS ===\n")
            log.write("the following SRR's have been annotated:\n")
            for srr in got_annotated:
                log.write(f"\t{srr}\n")
            log.write("the following SRR's have NOT been annotated, because they contain empty contigs from assembly:\n")
            for srr in not_annotated:
                log.write(f"\t{srr}\n")
            log.write(f"total annotation time (not incl. combination count): {str(round(timeend - timestart, 3))}s\n")
        print('results of annotation have been written to annotations/log.txt')


    # IMPORTANT CHANGE
    # this version of count_combinations only accounts for the first and best match of each gene in the
    # out_card.tsv and out_metacompare.tsv files. the previous version accounted for every match.
    def count_combinations(self):
        print('now counting the combinations...')
        timestart = timer()

        # {combo: count}
        combinations_table = {}

        # get contig folders
        result = subprocess.getoutput(f'ls {self.proj_path}/annotations')
        contigs = result.split('\n')
        contigs.remove('log.txt')

        # parse thru each contig folder, combining CARD and metacompare (will add larsson later)
        curr_contig = 1
        num_contigs = len(contigs)
        for contig in contigs:
            print(f'counting combos for contig: {contig} ({curr_contig}/{num_contigs})')
            curr_contig += 1

            card = open(f'{self.proj_path}/annotations/{contig}/out_card.tsv', 'r')
            card_tsv = csv.reader(card, delimiter='\t')
            metacompare = open(f'{self.proj_path}/annotations/{contig}/out_metacompare.tsv', 'r')
            metacompare_tsv = csv.reader(metacompare, delimiter='\t')

            currARG = '' # used to determine if ARG is first match; only considers it if yes
            alreadyARG = [] # used to indicate ARG is already looked at (in case of multiple)
            for row in card_tsv:
                if row[0] == currARG:
                    continue
                currARG = row[0]
                ARG = row[1]
                if ARG in alreadyARG:
                    continue
                alreadyARG.append(ARG)
                currMGE = '' # used to determine if MGE is first match; only considers it if yes
                alreadyMGE = [] # used to indicate MGE is already looked at (in case of multiple)
                for row2 in metacompare_tsv:
                    if row2[0] == currMGE:
                        continue
                    currMGE = row2[0]
                    MGE = row2[1]
                    if MGE in alreadyMGE:
                        continue
                    alreadyMGE.append(MGE)
                    combo = ARG + '\t' + MGE
                    # if combo is in table, increment count; otherwise, add to table
                    if combo in combinations_table:
                        combinations_table[combo] += 1
                    else:
                        combinations_table[combo] = 1
                metacompare.seek(0) # have to re-seek to start of file for it to work

            card.close()
            metacompare.close()

        # output results to tsv
        finale = open(f'{self.proj_path}/annotations/combinations.tsv', 'w')
        finale.write("ARG\tMGE\tcount\n")
        for combo in combinations_table:
            finale.write(combo + "\t" + str(combinations_table[combo]) + "\n")

        finale.close()

        timeend = timer()
        print(f'done counting... that took {timeend - timestart} seconds')



if __name__=="__main__":
    proj_path = sys.argv[1]  # 1st argument should be project name
    diamondDvr = DiamondDriver(proj_path)
    diamondDvr.run_diamond()
    diamondDvr.count_combinations()
