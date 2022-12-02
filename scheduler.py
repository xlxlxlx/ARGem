'''
- SCHEDULER CHANGES:
  - recently moved to agroseek/www/wp-includes/task_scheduler... hooray!
- to run: ./runscheduler.sh <metadata file> <project ID> <user ID> <mge_db>
  - (EX)  ./runscheduler.sh sample_metadata_upload_2.xlsx myProject myUser metacompare
'''

import luigi
import subprocess
import time
import json
from time import localtime, strftime
import calendar
import glob
# from datetime import datetime


# user projects stored under here!
userprojs_path = "userprojects"

ts = calendar.timegm(time.gmtime())

# paths to json files used for projects queue / completed projects -- used by status page
proj_q_path = "projects_queue.json"
comp_projs_path = "completed_projects.json"

#connect to db
import db_config as config
from os.path import dirname
import os

import pymysql
#import datetime
#import uuid

db = config.DATABASE

available_mge_db = ['metacompare','larsson','mobileOG']
default_mge_db = 'mobileOG'

try:
    connection = pymysql.connect(host = db['host'],
                    user = db['account'],
                    password = db['pwd'],
                    db = db['db_name'])

    cursor = connection.cursor()
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise




# paths to all the driver scripts -- right now they are all contained in the task_scheduler folder
path_to_sraretrieval = "driver_retrieval"
path_to_assembly = "driver_assembly"
path_to_annotation = "driver_annotation"
path_to_readmatching = "driver_readmatching"
path_to_analysis = "driver_analysis"


class PreCheck(luigi.Task):
    '''initiates the pipeline by checking if other projects are in queue'''

    metadata = luigi.Parameter()
    proj_ID = luigi.Parameter()
    user_ID = luigi.Parameter()
    database = luigi.Parameter()
    task_ID = luigi.Parameter()
    #userproj_dir = f"{userprojs_path}/project_{proj_ID}_{ts}"

  
    def output(self):
        # outcome of tasks stored in this file
        return luigi.LocalTarget(f"{userprojs_path}/project_{self.proj_ID}_{ts}/outcome.json")
    
    def run(self):
    
        # canceled task checker
        sql = "SELECT * FROM `project_tasks` WHERE task_id = %s"
        cursor.execute(sql, (self.task_ID))
        rows = cursor.fetchall()
        print(rows)
    
        if len(rows) == 0:
            exit()
    
        
        sql = "SELECT name FROM `project_prime` WHERE project_id = %s"
        cursor.execute(sql, (self.proj_ID))
        names = cursor.fetchall()
                     
        proj_name = names[0][0]
        print('====== project name: ' + proj_name + '=======')

        # add project to queue (json)
        with open(proj_q_path, 'r+') as pq_file:
            data = json.load(pq_file)
            sub_time = strftime("%b %d, %Y %H:%M:%S", localtime())
            curr_project = {"proj_ID": self.proj_ID, "proj_name": proj_name, "user_ID":self.user_ID, "sub_time":sub_time, "status":"PENDING", "database":self.database, "task_ID":self.task_ID}
            data['projects'].append(curr_project)
            pq_file.seek(0)
            json.dump(data, pq_file, indent=4)
            pq_file.truncate()

            #get <metadata file>
            #sql = "SELECT `Input_File_ID` FROM `project_tasks` WHERE `Status` = 'Pending' ORDER BY `Timestamp` DESC"
            #cursor.execute(sql)
            #rows = cursor.fetchall()
            #for row in rows:
            #        self.metadata = row
                    #break

            #get <project ID>
            #sql = "SELECT `Project_ID` FROM `project_tasks` WHERE `Status` = 'Pending' ORDER BY `Timestamp` DESC"
            #cursor.execute(sql)
            #rows = cursor.fetchall()
            #for row in rows:
            #        self.proj_ID = row
                    #break

            #get <user ID>
            #sql = "SELECT `Creator_ID` FROM `project_prime` WHERE `Project_ID` = %s"
            #cursor.execute(sql, (self.proj_ID))
            #rows = cursor.fetchall()
            #for row in rows:
            #        self.user_ID = row

            #get <mge database>
            #sql = "SELECT * FROM `project_tasks` WHERE `Status` = 'Pending' ORDER BY `Timestamp` DESC"
            #cursor.execute(sql)
            #rows = cursor.fetchall()
            #for row in rows:
            #        self.database = row
                    #break

            # now we use batch to handle the queue
            # while data['projects'][0] != curr_project:
            #     print("other projects are in the queue! please wait...")
            #     time.sleep(5)
            #     pq_file.seek(0)
            #     data = json.load(pq_file)

        # somehow the mkdir didn't work so a temperary fix here
        os.mkdir(f"{userprojs_path}/project_{self.proj_ID}_{ts}")
        print(f"{userprojs_path}/project_{self.proj_ID}_{ts}") 
        
        # create outcome.json and set default values
        with self.output().open('w') as fout:
        #with open(f"{userprojs_path}/project_{self.proj_ID}/outcome.json", 'w') as fout:
            print("precheck step: writing to output json file")    
            print(fout.name)
            data = {}
            
            data['retrieval_outcome'] = 'N/A'
            data['assembly_outcome'] = 'N/A'
            data['annotation_outcome'] = 'N/A'
            data['analysis_outcome'] = 'N/A'


            json.dump(data, fout, indent=4)

        # copy metadata spreadsheet to project folder
        subprocess.run(f'cp {self.metadata} {userprojs_path}/project_{self.proj_ID}_{ts}', shell=True)


class RetrieveSRA(luigi.Task):
    '''calls SRA retrieval driver'''

    metadata = luigi.Parameter()
    proj_ID = luigi.Parameter()
    user_ID = luigi.Parameter()
    database = luigi.Parameter()
    task_ID = luigi.Parameter()

    #userproj_dir = f"{userprojs_path}/project_{proj_ID}_{ts}"

    def requires(self):
        return PreCheck(self.metadata, self.proj_ID, self.user_ID, self.database, self.task_ID)

    def output(self):
        return luigi.LocalTarget(f"{userprojs_path}/project_{self.proj_ID}_{ts}/done_sraretrieval.txt")
    
    def run(self):
        # canceled task checker
        sql = "SELECT * FROM `project_tasks` WHERE task_id = %s"
        cursor.execute(sql, (self.task_ID))
        rows = cursor.fetchall()
        print(rows)
    
        if len(rows) == 0:
            exit()

        sql = "UPDATE `project_tasks` SET `status` = 'SRA-RETRIEVAL' WHERE task_id = %s"
        cursor.execute(sql, (self.task_ID))
                           
        connection.commit()

        sql = "UPDATE `project_tasks` SET `Output_File_ID` = %s WHERE task_id = %s"
        cursor.execute(sql, (f'/agroseek/www/wp-includes/task_scheduler/{userprojs_path}/project_{self.proj_ID}_{ts}/', self.task_ID))
                           
        connection.commit()


        # update projects queue
        with open(proj_q_path, 'r+') as pq_file:
            data = json.load(pq_file)
            data['projects'][0]["status"] = "SRA-RETRIEVAL"
            pq_file.seek(0)
            json.dump(data, pq_file, indent=4)
            pq_file.truncate()

        # call driver
        subprocess.run(f'python3 {path_to_sraretrieval}/sra_retriever.py {self.metadata} {userprojs_path}/project_{self.proj_ID}_{ts} {self.user_ID} {self.task_ID}', shell=True)

        with self.output().open('w') as fout:
            fout.write("SRA retrieval complete.\n")
        
        # Remove tmp files
        subprocess.run(f"rm -rf {path_to_sraretrieval}/../fasterq.tmp.*", shell=True)


class ShortReadsMatching(luigi.Task):
    '''calls SRA retrieval driver'''

    metadata = luigi.Parameter()
    proj_ID = luigi.Parameter()
    user_ID = luigi.Parameter()
    database = luigi.Parameter()
    task_ID = luigi.Parameter()

    # userproj_dir = f"{userprojs_path}/project_{proj_ID}_{ts}"

    def requires(self):
        return RetrieveSRA(self.metadata, self.proj_ID, self.user_ID, self.database, self.task_ID)

    def output(self):
        return luigi.LocalTarget(f"{userprojs_path}/project_{self.proj_ID}_{ts}/done_shortreads.txt")

    def run(self):
        # canceled task checker
        sql = "SELECT * FROM `project_tasks` WHERE task_id = %s"
        cursor.execute(sql, (self.task_ID))
        rows = cursor.fetchall()
        print(rows)

        if len(rows) == 0:
            exit()

        sql = "UPDATE `project_tasks` SET `status` = 'SHORT-READS-MATCHING' WHERE task_id = %s"
        cursor.execute(sql, (self.task_ID))
                           
        connection.commit()


        # update projects queue
        # (TODO) update this together with the status queue
        # with open(proj_q_path, 'r+') as pq_file:
        #     data = json.load(pq_file)
        #     data['projects'][0]["status"] = "SHORT-READS-MATCHING"
        #     pq_file.seek(0)
        #     json.dump(data, pq_file, indent=4)
        #     pq_file.truncate()

        # call driver
        with open(f"{userprojs_path}/project_{self.proj_ID}_{ts}/outcome.json", "r") as outcome_file:
            data = json.load(outcome_file)
            # case 1: retrieval didn't run or failed --> don't run assembly
            if data['retrieval_outcome'] == 'N/A' or data['retrieval_outcome'] == 'Failure':
                print(f"could not run read matching due to SRA retrieval outcome: {data['retrieval_outcome']}")
            # case 2: retrieval succeeded --> run assembly
            else:
                subprocess.run(f'python3 {path_to_readmatching}/diamond_driver.py {userprojs_path}/project_{self.proj_ID}_{ts}', shell=True)
                print("found_annotated_file: " + str(len(glob.glob(f'{userprojs_path}/project_{self.proj_ID}_{ts}/shortreads_output/*.clean.card.matches.quant.normalization'))))
                if len(glob.glob(f'{userprojs_path}/project_{self.proj_ID}_{ts}/shortreads_output/*.clean.card.matches.quant.normalization')) > 0:
                    subprocess.run(f'python3 normalization2combined.py {userprojs_path}/project_{self.proj_ID}_{ts}/shortreads_output/', shell=True)
        with self.output().open('w') as fout:
            fout.write("Short reads matching complete.\n")


class AssembleIt(luigi.Task):
    '''calls assembly driver'''

    metadata = luigi.Parameter()
    proj_ID = luigi.Parameter()
    user_ID = luigi.Parameter()
    database = luigi.Parameter() 
    task_ID = luigi.Parameter()

    #userproj_dir = f"{userprojs_path}/project_{proj_ID}_{ts}"

    def requires(self):
       return ShortReadsMatching(self.metadata, self.proj_ID, self.user_ID, self.database, self.task_ID) 
       #return RetrieveSRA(self.metadata, self.proj_ID, self.user_ID, self.database, self.task_ID)

    def output(self):
        return luigi.LocalTarget(f"{userprojs_path}/project_{self.proj_ID}_{ts}/done_assembly.txt")

    def run(self):
        # canceled task checker
        sql = "SELECT * FROM `project_tasks` WHERE task_id = %s"
        cursor.execute(sql, (self.task_ID))
        rows = cursor.fetchall()
        print(rows)
    
        if len(rows) == 0:
            exit()

        sql = "UPDATE `project_tasks` SET `status` = 'ASSEMBLY' WHERE task_id = %s"
        cursor.execute(sql, (self.task_ID))
                           
        connection.commit()

        # update projects queue
        with open(proj_q_path, 'r+') as pq_file:
            data = json.load(pq_file)
            data['projects'][0]["status"] = "ASSEMBLY"
            pq_file.seek(0)
            json.dump(data, pq_file, indent=4)
            pq_file.truncate()

        # call driver
        with open(f"{userprojs_path}/project_{self.proj_ID}_{ts}/outcome.json", "r") as outcome_file:
            print("assembly step: writing to output json file")    
            print(outcome_file.name)
            data = json.load(outcome_file)
            # case 1: retrieval didn't run or failed --> don't run assembly
            if data['retrieval_outcome'] == 'N/A' or data['retrieval_outcome'] == 'Failure':
                print(f"could not run assembly due to SRA retrieval outcome: {data['retrieval_outcome']}")
            # case 2: retrieval succeeded --> run assembly
            else:
                subprocess.run(f'python3 {path_to_assembly}/megahit_driver.py {userprojs_path}/project_{self.proj_ID}_{ts}', shell=True)

        with self.output().open('w') as fout:
            fout.write("assembly complete.\n")


class AnnotateIt(luigi.Task):
    '''calls annotation driver'''

    metadata = luigi.Parameter()
    proj_ID = luigi.Parameter()
    user_ID = luigi.Parameter()
    database = luigi.Parameter()
    task_ID = luigi.Parameter()

    #userproj_dir = f"{userprojs_path}/project_{proj_ID}_{ts}"

    def requires(self):
        return AssembleIt(self.metadata, self.proj_ID, self.user_ID, self.database, self.task_ID)

    def output(self):
        return luigi.LocalTarget(f"{userprojs_path}/project_{self.proj_ID}_{ts}/done_annotation.txt")
    
    def run(self): 
        # canceled task checker
        sql = "SELECT * FROM `project_tasks` WHERE task_id = %s"
        cursor.execute(sql, (self.task_ID))
        rows = cursor.fetchall()
        print(rows)
    
        if len(rows) == 0:
            exit()

        sql = "UPDATE `project_tasks` SET `status` = 'ANNOTATION' WHERE task_id = %s"
        cursor.execute(sql, (self.task_ID))
                           
        connection.commit()        
               

        # update projects queue
        with open(proj_q_path, 'r+') as pq_file:
            data = json.load(pq_file)
            data['projects'][0]["status"] = "ANNOTATION"
            pq_file.seek(0)
            json.dump(data, pq_file, indent=4)
            pq_file.truncate()

        # call driver
        with open(f"{userprojs_path}/project_{self.proj_ID}_{ts}/outcome.json", "r") as outcome_file:
            data = json.load(outcome_file)
            # case 1: assembly didn't run or failed --> don't run annotation
            if data['assembly_outcome'] == 'N/A' or data['assembly_outcome'] == 'Failure':
                print(f"could not run annotation due to assembly outcome: {data['assembly_outcome']}")
            # case 2: assembly succeeded --> run annotation
            # mge databases

            # do not terminate the pipeline if the mge database is incorrect. Use default. 
            if (self.database not in available_mge_db):
                print("Invalid database: {self.database}. Use default database: " + default_mge_db)
                self.database = default_mge_db

            print("Starting annotation using " + self.database + " database")
            subprocess.run(f'python3 {path_to_annotation}/annotation_driver.py {userprojs_path}/project_{self.proj_ID}_{ts} {self.database}', shell=True)


        # put all the sample's annotation together
        subprocess.run(f'python3 long_contig_annotation_combined.py {userprojs_path}/project_{self.proj_ID}_{ts}/annotations', shell=True)

        with self.output().open('w') as fout:
            fout.write("annotation complete.\n")


        #cp_cmd = "cp " + f"{userprojs_path}/project_{self.proj_ID}_{ts}/annotations/combinations.tsv " + f"/agroseek/www/wp-content/upload/user_{self.user_ID}/project_{self.proj_ID}/project_annotations_result.tsv"
        #print(cp_cmd)
        #os.system(cp_cmd)

class AnalyzeIt(luigi.Task):
    '''calls annotation driver'''

    metadata = luigi.Parameter()
    proj_ID = luigi.Parameter()
    user_ID = luigi.Parameter()
    database = luigi.Parameter()
    task_ID = luigi.Parameter()
    
    #proj_output = luigi.LocalTarget(f"{userprojs_path}/project_{proj_ID}_{ts}/outcome.json")

    # userproj_dir = f"{userprojs_path}/project_{proj_ID}_{ts}"

    def requires(self):
        return AnnotateIt(self.metadata, self.proj_ID, self.user_ID, self.database, self.task_ID)

    def output(self):
        return luigi.LocalTarget(f"{userprojs_path}/project_{self.proj_ID}_{ts}/done_analysis.txt")

    def run(self):
        # canceled task checker
        sql = "SELECT * FROM `project_tasks` WHERE task_id = %s"
        cursor.execute(sql, (self.task_ID))
        rows = cursor.fetchall()
        print(rows)
    
        if len(rows) == 0:
            exit()

        sql = "UPDATE `project_tasks` SET `status` = 'ANALYSIS' WHERE task_id = %s"
        cursor.execute(sql, (self.task_ID))
                           
        connection.commit()        
        

        # update projects queue
        with open(proj_q_path, 'r+') as pq_file:
            data = json.load(pq_file)
            data['projects'][0]["status"] = "ANALYSIS"
            pq_file.seek(0)
            json.dump(data, pq_file, indent=4)
            pq_file.truncate()


        print("Starting analyzing")

        # co-occurrence
        print(f'python3 {path_to_analysis}/co_occurrence_to_html.py {path_to_analysis}/CARD_classification_id.csv {userprojs_path}/project_{self.proj_ID}_{ts}/annotations/combinations.tsv {userprojs_path}/project_{self.proj_ID}_{ts}/co_occurrence.html 3')
        subprocess.run(
            f'python3 {path_to_analysis}/co_occurrence_to_html.py {path_to_analysis}/CARD_classification_id.csv {userprojs_path}/project_{self.proj_ID}_{ts}/annotations/combinations.tsv {userprojs_path}/project_{self.proj_ID}_{ts}/co_occurrence.html 3',            
            shell=True)
            
        # correlation
        subprocess.run(
            f'python3 {path_to_analysis}/SAIG_correlation.py {userprojs_path}/project_{self.proj_ID}_{ts}/shortreads_output/combined.clean.card.matches.quant.normalization.16S.csv {userprojs_path}/project_{self.proj_ID}_{ts}/correlation_result.csv',            
            shell=True)
        subprocess.run(
            f'python3 {path_to_analysis}/correlation_to_html.py {userprojs_path}/project_{self.proj_ID}_{ts}/correlation_result.csv {userprojs_path}/project_{self.proj_ID}_{ts}/correlation.html {path_to_analysis}/CARD_classification_id.csv',            
            shell=True)

            
        # change the result once the analysis script is resolved
        # write to outcome.json
        with open(f"{userprojs_path}/project_{self.proj_ID}_{ts}/outcome.json", "r+") as outcome_file:
            data = json.load(outcome_file)
            # success by default, will account for errors later!
            data['analysis_outcome'] = 'Success'
            outcome_file.seek(0)
            json.dump(data, outcome_file, indent=4)
            outcome_file.truncate()


        with self.output().open('w') as fout:
            fout.write("analysis complete.\n")


class Runner(luigi.Task):
    '''runner task for the pipeline'''

    metadata = luigi.Parameter()
    proj_ID = luigi.Parameter()
    user_ID = luigi.Parameter()
    database = luigi.Parameter(default=default_mge_db)
    task_ID = luigi.Parameter()

    #userproj_dir = f"{userprojs_path}/project_{proj_ID}_{ts}"

    def requires(self):
        #return AnnotateIt(self.metadata, self.proj_ID, self.user_ID, self.database, self.task_ID)
        return AnalyzeIt(self.metadata, self.proj_ID, self.user_ID, self.database, self.task_ID)

    def output(self):
        return luigi.LocalTarget(f"{userprojs_path}/project_{self.proj_ID}_{ts}/done.txt")

    def run(self):

        # canceled task checker
        sql = "SELECT * FROM `project_tasks` WHERE task_id = %s"
        cursor.execute(sql, (self.task_ID))
        rows = cursor.fetchall()
        print(rows)

        if len(rows) == 0:
            exit()


        sql = "SELECT name FROM `project_prime` WHERE project_id = %s"
        cursor.execute(sql, (self.proj_ID))
        names = cursor.fetchall()
        #print(names)
        proj_name = names[0][0]
        print('====== project name: ' + proj_name + '=======')

        # pop project from queue
        with open(proj_q_path, 'r+') as pq_file:
            data = json.load(pq_file)
            del data['projects'][0]
            pq_file.seek(0)
            json.dump(data, pq_file, indent=4)
            pq_file.truncate()

        # add project to completed projects (json)
        with open(comp_projs_path, 'r+') as cp_file:
            data = json.load(cp_file)
            comp_time = strftime("%b %d, %Y %H:%M:%S", localtime())
            with open(f"{userprojs_path}/project_{self.proj_ID}_{ts}/outcome.json", "r") as outcome_file:  # read the outcome for each task
                outcomeData = json.load(outcome_file)
                outcome = [outcomeData['retrieval_outcome'], outcomeData['assembly_outcome'], outcomeData['annotation_outcome'], outcomeData['analysis_outcome']]
            curr_project = {"proj_name":proj_name, "user_ID":self.user_ID, "comp_time":comp_time, "outcome":outcome, "database":self.database, "proj_ID": self.proj_ID}
            data['projects'].insert(0, curr_project)
            cp_file.seek(0)
            json.dump(data, cp_file, indent=4)
            cp_file.truncate()
                    
            sql = "UPDATE `project_tasks` SET `status` = %s WHERE `task_ID` = %s"
            cursor.execute(sql, ('Done', self.task_ID))
            connection.commit()

        with self.output().open('w') as fout:
            fout.write("pipeline complete.\n")
