
'''
File Structure (temp)
    - driver_retrieval/
        - sra_retriever.py
        - SRA-Numbers
            - sra-log.tsv
            - error-log.tsv
            - private-sra-log.tsv
            - invalid-sra-log.tsv
            - validation-error-log.tsv

    - /tools/sratoolkit.2.10.8/bin/
        - prefetch-orig.x.xx.x
        - fastq-dump.x.xx.x
'''

import re
import os
import sys
import time
# import pymysql
import datetime
import subprocess
import pandas as pd
import json

class SequenceRetriever:
    '''
    Class responsible for retrieving the sequence data and verifying the validity of the .sra files
    after download. Both the file conversion (.sra to .fastq) and the validation process is dependent
    on SRA Toolkit's VDB module. 
    '''

    def __init__(self, proj_path):

        # this is the project folder the results are outputted
        self.proj_path = proj_path

        self.dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'SRA-Numbers') # log file path
        self.sra_toolkit_path = '' # SRA Toolkit path

        self.output_dir = f"{proj_path}/raw_sequence_data" # sequence data output directory name
        self.errorLogFilename = "error-log.tsv"
        self.SRALogFilename = "sra-log"

        self.data_hash_table = {}

        self.prefetch_access_denied_sra = []
        self.prefetch_access_failed_sra = []
        self.prefetch_oversize_sra = []



    def download_data(self, sra_list: list):
        '''
        Download the raw sequence data from the corresponding SRA accession numbers using the SRA Toolkit.

        :param sra_list: a list of SRA accession numbers to retrieve to raw sequence data of
        '''
        for sra_num in sra_list:

            curr_time = time.strftime("%Y-%m-%d|%H:%M:%S")

            print('\n\n')
            vdb_dump_output = subprocess.getoutput(f"{self.sra_toolkit_path}/vdb-dump --info {sra_num}")
            if self.check_proccess_output(sra_num, "vdb-dump", vdb_dump_output) == -1:
                for line in vdb_dump_output.split('\n'):
                    print(line)
            else: continue

            max_prefetch_size = '70G' # in bytes (or with GB)
            subprocess.run(f"{self.sra_toolkit_path}/prefetch -p {sra_num} -X {max_prefetch_size}", shell=True)

            # check if the prefetched .sra file exist (if not, then it might have exceeded the max-size requirement)
            if sra_num not in os.listdir():
                self.prefetch_oversize_sra.append(sra_num)
                continue

            print(f"Converting {sra_num}.sra to {sra_num}.fastq...")
            subprocess.run(f"{self.sra_toolkit_path}/fasterq-dump --split-3 -O {self.output_dir}/{sra_num} \
                ./{sra_num}/{sra_num}.sra -p", shell=True)


    def verify_sra_format(self, sra_input: list) -> list:
        '''
        Verifies the input SRA accession numbers to ensure that their format is valid. SRA numbers with invalid format will be
        removed from the list of correct SRA numbers. Errors will be logged.

        :param sra_data: a list of SRA numbers to be verified
        :return: a list containing the correctly formatted SRA numbers
        :rtype: list
        '''
        correct_data = []
        incorrect_data = []
        # past_data = [] # list of sra numbers that has been previously retrieved (duplicates will be dropped)

        # mycursor = self.DATABASE.cursor()
        # sql_retrieve_sra = f'SELECT SRA FROM SRA_record;'
        # mycursor.execute(sql_retrieve_sra)
        # past_data = [sra[0] for sra in mycursor]

        for sra_num in sra_input:
            sra_num = sra_num.strip().replace('\n', '')

            # if re.match("^(SRR|ERR)[0-9]+$", sra_num.upper()) and sra_num not in past_data: # i.e. SRR1568808
            if re.match("^(SRR|ERR)[0-9]+$", sra_num.upper()): # i.e. SRR1568808
                correct_data.append(sra_num)
                        
            # elif sra_num in past_data:
            #     incorrect_data.append(sra_num)
            #     errorMess = "Previously Processed SRA"
            #     print(f"SRA number {sra_num} has already been processed before.")

            #     # TODO: needs to log this error
            else:
                incorrect_data.append(sra_num)
                errorMess = "Incorrect Formatting"
                print(f"SRA number {sra_num} is incorrect.")

                # invalide SRA log
                self.log_error(sra_num, errorMess, "404")

        return correct_data



    def validate_sra_data(self, sra_input_list: list, task_id: str) -> bool:
        '''
        Validates the downloaded .sra files using the SRA Toolkit. Errors will be logged.

        :param sra_input_list: a list of SRA numbers to be validated
        :return: false if any data failed to be validated and true otherwise
        :rtype: boolean
        '''
        errors = []
        validation = True

        for sra_num in self.progress_bar(sra_input_list, prefix="Validating SRA Data: ", bar_length=50):
            result = subprocess.getoutput(f'{self.sra_toolkit_path}/vdb-validate {sra_num}')
            result = result.split('\n')

            for line in result:
                if re.search("[a-zA-Z0-9] ok$", line, re.IGNORECASE) != None \
                    or re.search(" reads$", line, re.IGNORECASE) != None \
                    or re.search("is consistent$", line, re.IGNORECASE) != None:
                    continue
                else:
                    err = ""
                    if sra_num in self.prefetch_access_denied_sra:
                        err = "Project is private: Access Denied (403)"
                        errors.append(f'Data {sra_num} validation failed. Error: {err}')

                    elif sra_num in self.prefetch_access_failed_sra:
                        err = "Incorrect SRA: failed to resolve accession (404)"
                        errors.append(f'Data {sra_num} validation failed. Error: {err}')

                    elif sra_num in self.prefetch_oversize_sra:
                        err = "SRA size exceeds the maximum allowed size (1101)"
                        errors.append(f'Data {sra_num} validation failed. Error: {err}')

                    elif len(line) > 0:
                        err = line
                        errors.append(f'Error Not Caught: Data {sra_num} validation failed. Error: {err}')

                    validation = False
                    self.log_error(sra_num, err, "validation-failure", task_id)

        for e in errors:
            print(e)

        return validation


    def check_proccess_output(self, sra_num: str, process: str, process_output: str) -> int:
        '''
        Function for identifying the process's error. Determines whether a vdb-dump failure is caused by invalid
        SRA accession numbers or SRAs to private projects.

        :param sra_num: SRA number used during the process
        :param process: name of the process
        :param process_output: the shell output for the process
        :return: 403 for access denied
                 404 for failed to resolve number
                 1101 for SRA size exceeding max allowed
                 -1 if no error is found
        '''
        process_output = process_output.strip().split('\n')

        if process == "vdb-dump":
            if re.search(" Access denied ", process_output[0], re.IGNORECASE) != None \
                and re.search("( 403 )", process_output[0], re.IGNORECASE) != None:

                print(f'Error: Access denied for {sra_num}. (403)')
                self.prefetch_access_denied_sra.append(sra_num)
                return 403

            elif re.search(" failed to resolve accession ", process_output[0], re.IGNORECASE) != None \
                and re.search("( 404 )", process_output[0], re.IGNORECASE) != None:

                print(f'Error: Failed to resolve accession number {sra_num}. (404)')
                self.prefetch_access_failed_sra.append(sra_num)
                return 404

        elif process == 'prefetch':
            if re.search("is larger than maximum allowed: skipped", process_output[1], re.IGNORECASE) != None:
                return 1101

        elif process == "fasterq-dump":
            pass

        return -1


    def log_error(self, sra_num: str, error_message: str, error_id: str, task_id: str):
        '''
        Log errors to the correspounding file. 
        Error log format: Error_Time\tSRA_Accession_Number\tProject_ID\tUser_ID\tError_Reason

        :param sra_num: the SRA accession number where the error originated from
        :param error_message: a message explaining what the error is (the error generated by a certain command)
        :param error_id: error code/name used to identify the error
        '''
        # Default Error Log (all errors will be logged)
        with open(os.path.join(self.dir_path, self.errorLogFilename), "a+", encoding="utf-8") as file_ptr: 
            label = "Error_Time\tSRA_Accession_Number\tProject_ID\tUser_ID\tError_Reason\n"
            file_ptr.seek(0)
            firstline = file_ptr.readline()
            if firstline != label:
                file_ptr.write(label)

            errorTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file_ptr.write(f"{errorTime}\t{sra_num}\t")
            for data in self.data_hash_table[sra_num]:
                file_ptr.write(f"{data}\t")
            file_ptr.write(f'{error_message}\n')

        if not os.path.exists(f'/agroseek/www/wp-includes/task_scheduler/sra_log/{task_id}'): 
            os.mkdir(f'/agroseek/www/wp-includes/task_scheduler/sra_log/{task_id}')
        # Separate Error Log
        error_log_file = ""
        if error_id == "404":
            error_log_file = f'invalid-sra-log.tsv'
        elif error_id == "403":
            error_log_file = f'private-sra-log.tsv'
        elif error_id == "1101":
            error_log_file = f'oversize-sra-log.tsv'
        elif error_id == 'validation-failure':
            error_log_file = f'validation-error-log.tsv'
        else: print(f'Error >{error_message}({error_id})< for SRA {sra_num} will not be reflected in any distinct error log files. Please visit "{self.errorLogFilename}" for the error.')

        if len(error_log_file) > 0:
            with open(f"/agroseek/www/wp-includes/task_scheduler/sra_log/{task_id}/{error_log_file}", "w+", encoding="utf-8") as file_ptr: 
                label = "Error_Time\tSRA_Accession_Number\tProject_ID\tUser_ID\tError_Reason\n"
                file_ptr.seek(0)
                firstline = file_ptr.readline()
                if firstline != label:
                    file_ptr.write(label)

                errorTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                file_ptr.write(f"{errorTime}\t{sra_num}\t")
                for data in self.data_hash_table[sra_num]:
                    file_ptr.write(f"{data}\t")
                file_ptr.write(f'{error_message}\n')


    def read_SRA_log(self):
        '''
        Reads the SRA accession number log file and stores the data in a hash table.
        '''
        with open(os.path.join(self.dir_path, self.SRALogFilename), "r", encoding="utf-8") as file_ptr:
            content = file_ptr.readlines()
            for line in content:
                values = line.replace("\n", "").split("\t")
                self.data_hash_table[values[0].strip()] = values[1:len(values)]


    def cleanup_files(self, sra_data: dict, task_id:str):
        '''
        Removes all redundant .sra files that are no longer needed. Failed removal will be logged accordingly.

        :param sra_data: dictionary containing the sra data (including the sra numbers)
        '''
        errors = []

        for sra_num in self.progress_bar(sra_data, prefix="Cleaning Up Redundant Files: ", bar_length=50):
            sra_num = sra_num.strip().replace('\n', '')

            # Failed SRA prefetch does not create a empty file
            if sra_num in self.prefetch_access_failed_sra or sra_num in self.prefetch_access_denied_sra or sra_num in self.prefetch_oversize_sra:
                continue

            file_removal = subprocess.getoutput(f'rm ./{sra_num}/{sra_num}.sra')
            dir_removal = subprocess.getoutput(f'rmdir ./{sra_num}')

            if len(file_removal) > 0 or len(dir_removal) > 0:
                errors.append(f"Removal for {sra_num}.sra failed.")
                error_message = f"{sra_num}.sra and/or the folder containing this file failed to be removed."
                self.log_error(sra_num, error_message, "-1", task_id) 


        if len(self.prefetch_access_denied_sra) > 0:
            for sra_num in self.prefetch_access_denied_sra:
                empty_folder_removal = subprocess.getoutput(f'rmdir {os.path.dirname(os.path.realpath(__file__))}/{self.output_dir}/{sra_num}')

                error_message = "Incorrect SRA: access denied (403)"
                self.log_error(sra_num, error_message, "403", task_id)

        if len(self.prefetch_access_failed_sra) > 0:
            for sra_num in self.prefetch_access_failed_sra:
                empty_folder_removal = subprocess.getoutput(f'rmdir {os.path.dirname(os.path.realpath(__file__))}/{self.output_dir}/{sra_num}')

                error_message = "Incorrect SRA: failed to resolve accession (404)"
                self.log_error(sra_num, error_message, "404", task_id)

        if len(self.prefetch_oversize_sra) > 0:
            for sra_num in self.prefetch_oversize_sra:
                empty_folder_removal = subprocess.getoutput(f'rmdir {os.path.dirname(os.path.realpath(__file__))}/{self.output_dir}/{sra_num}')

                error_message = "SRA exceeds the maximum allowed size (1101)"
                self.log_error(sra_num, error_message, "1101", task_id)

        for e in errors:
            print(e)


    def progress_bar(self, input, prefix="", suffix="", suffix_control=False, bar_length=50, file=sys.stdout):
        '''Light-weight progress bar (generator)

        :param input: list/range input to be iterated over
        :param prefix: prefix for the progress bar
        :param suffix: suffix for the progress bar
        :param suffix control: boolean to whether the suffix should be printed
        :param bar_length: the progress bar's length
        :param file: display/storage method
        '''

        count = len(input)
        def show(curr):
            filled_length = int(bar_length * curr / count)

            filled = filled_length * '#'
            unfilled = (bar_length - filled_length) * ' '

            if curr == count and suffix_control == True:
                file.write(f"{prefix}|{filled}{unfilled}| {curr}/{count} {suffix}\r")
            else:
                file.write(f"{prefix}|{filled}{unfilled}| {curr}/{count}\r")
            file.flush()

        show(0)
        for curr, val in enumerate(input):
            yield val
            show(curr + 1)
        file.write("\n")
        file.flush()



    def run_retriever(self, verify_input=False, validate_data=False, task_id='000000'):
        '''
        Pre-built function for running the SRA retriever directly.

        :param verify_input: gate to a pre-download verification on user inputted SRA accession numbers
        :param validate_data: gate to a post-download validation to the downloaded .sra files 
        '''
        start_time = time.time()

        self.read_SRA_log()

        sra_list = []
        for key in self.data_hash_table:
            sra_list.append(key.strip())
        if verify_input == True:
            sra_list = self.verify_sra_format(sra_list)

        self.download_data(sra_list)

        if validate_data == True:
            self.validate_sra_data(sra_list, task_id)

        self.cleanup_files(sra_list, task_id)

        time_spent = round((time.time() - start_time), 2)
        print(f"\nDownload Completed :) [{time_spent} seconds]")

        # write to outcome.json
        with open(f"{self.proj_path}/outcome.json", "r+") as outcome_file:
            data = json.load(outcome_file)
            # success by default, will account for errors later!
            data['retrieval_outcome'] = 'Success'
            outcome_file.seek(0)
            json.dump(data, outcome_file, indent=4)
            outcome_file.truncate()


class SRARetriever:
    '''
    Class responsible for retrieving the SRA accession numbers from the user-uploaded metadata spreadsheets.
    '''
    def __init__(self):
        self.log_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'SRA-Numbers')
        self.log_file_name = "sra-log"

    def retrieve_SRA(self, sys_argv):
        '''
        Retrieves the SRA accession numbers from the metadata spreadsheets.

        :param sys_argv: Arguments provided from script execution.
            Argument One: Input file name
            Argument Two: Project ID
            Argument Three: User ID

        Execution reference: wp-content/themes/twentyseventeen/uploadmeta_submit.php
        '''
        if len(sys_argv) > 1:
            input_file = sys.argv[1]
        if len(sys_argv) > 2:
            project_id = sys.argv[2]
        if len(sys_argv) > 3:
            user_id = sys.argv[3]        
        if len(sys_argv) > 4:
            task_id = sys.argv[4]
        if len(sys_argv) > 5:
            print(f"Warning: Too many arguments given to {__file__}")

        xl = pd.ExcelFile(input_file, engine = 'openpyxl')

        if "Metadata" in xl.sheet_names:
            df_metadata = pd.read_excel(input_file, index_col=0, sheet_name='Metadata', engine = 'openpyxl')
        else:
            df_metadata = pd.read_excel(input_file, index_col=0, engine = 'openpyxl')
            
        df_metadata = df_metadata.apply(pd.to_numeric, errors='ignore')

        SRA_list = df_metadata["NCBI_SRA_number"].to_string(index=False).strip().split('\n')
        if SRA_list[0].startswith("SRR") != 1:
            SRA_list = SRA_list[1:]

        with open(os.path.join(self.log_file_path, self.log_file_name), "w", encoding="utf-8") as file_ptr:
            for SRA in SRA_list:
                file_ptr.write(f"{SRA}\t{project_id}\t{user_id}\n")


# Driver Code
if __name__ == "__main__":
    SRARetr = SRARetriever()
    SRARetr.retrieve_SRA(sys.argv)

    proj_path = sys.argv[2]  # 2nd argument should be project name
    print("====== proj_path:" + proj_path + "=======")
    task_id = sys.argv[4]
    SeqRetr = SequenceRetriever(proj_path)
    SeqRetr.run_retriever(verify_input=True, validate_data=True, task_id=task_id)


# If store the retrieved SRA accession numbers, uncomment the following block
# class SRARetriever:
#     '''
#     Class responsible for the retrieval and storage of SRA accession numbers from the MySQL database.
#     '''

#     def __init__(self):
#         self.query = 'select * from sample_metadata where ATT_ID = 234;'
#         self.SRAInfo = {}


#     def retrieve_sra_num(self):
#         '''
#         Retrieves SRA accession numbers from the MySQL database. All data present in the MySQL SRA table
#         will be stored in the self.SRAInfo hash table.

#         :return: a list containing the SRA accession numbers retrieved
#         :rtype: list
#         '''

#         database = pymysql.connect(
#             host='localhost',
#             user='root',
#             passwd='password',
#             database='sra_test'
#         )

#         mycursor = database.cursor()
#         try:
#             mycursor.execute(self.query)

#         except pymysql.Error as e:
#             print("Error reading data from MySQL table: ", e)

#         for sra in mycursor:
#             try:
#                 self.SRAInfo[sra[4]] = [sra[0], sra[1], sra[2], sra[3]]
#             except Exception as error:
#                 print(f"SRA info hash table write error for {sra[4]}: {error}")


#     def store_sra_num(self, log_file_name: str):
#         '''
#         Stores the retrieved SRA accession numbers in the designated log file

#         :param log_file_name: name for the txt file storing the SRA accession numbers
#         :param sra_list: a list of SRA accession numbers
#         '''
#         seqRetr = SequenceRetriever(self)
#         file_path = seqRetr.dir_path
        
#         with open(os.path.join(file_path, log_file_name), "w", encoding="utf-8") as file_ptr:
#             for sra, sra_info in self.SRAInfo.items():
#                 file_ptr.write(f"{sra}\n")
#             print(f"{len(self.SRAInfo.items())} SRA accession number(s) has been successfully written into the log file.")

    


