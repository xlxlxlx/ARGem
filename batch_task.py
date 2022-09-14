
import sys
import pymysql
import db_config as config
import os
import calendar
import time
import json
#from time import localtime, strftime

if __name__ == "__main__":

    db = config.DATABASE
    shell_path = "/agroseek/www/wp-includes/task_scheduler/runscheduler.sh"

    pending_projects = []
    queued_projects = []
    #proj_q_path = "../../wp-content/themes/twentyseventeen/projects_queue.json"

    try:
        connection = pymysql.connect(host=db['host'],
                                     user=db['account'],
                                     password=db['pwd'],
                                     db=db['db_name'])

        cursor = connection.cursor()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    path_prefix = '/agroseek/www/wp-content/upload/'

    sql = "SELECT project_id, user_id, input_file_id, MGE_DB, task_id FROM `project_tasks` WHERE status = 'pending' ORDER By timestamp ASC"
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(rows)


    #rows = (('5e42d4b8a97cb', 1, '/agroseek/www/wp-content/upload/user_1/project_5e42d4b8a97cb/metadata_624d54501fbbf.xlsx', 'metacompare'),
    #        ('5e42d4b8a97cb', 1, '/agroseek/www/wp-content/upload/user_1/project_5e42d4b8a97cb/metadata_624d545de83d3.xlsx', 'larsson'))

    if len(rows) == 0:
        exit()


    for row in rows:
        project_id = row[0]
        user_id = row[1]
        input_file = row[2]
        mge_db = row[3]

        task_id = row[4]

        project_task = f"{shell_path} {input_file} {project_id} {user_id} {mge_db} {task_id}"
        pending_projects.append(project_task)

        # demo purpose, comment out if not used
        #pending_projects.append('sleep 60')

        pending_projects.append('wget "https://agroseek.cs.vt.edu/index.php/send_email_sra/?project='+str(project_id)+'&user='+str(user_id)+'&task='+str(task_id)+'" --no-check-certificate')
        pending_projects.append('rm index.html*')


        #queued_projects.append(str(task_id))
        queued_projects.append("'"+str(task_id)+"'")

        #with open(proj_q_path, 'r+') as pq_file:
        #    data = json.load(pq_file)
        #    sub_time = strftime("%b %d, %Y %H:%M:%S", localtime())
        #    curr_project = {"proj_ID":project_id, "user_ID":user_id, "sub_time":sub_time, "status":"PENDING", "database":"default"}
        #    data['projects'].append(curr_project)
        #    pq_file.seek(0)
            #json.dump(data, pq_file, indent=4)



    ts = calendar.timegm(time.gmtime())
    task_list_tmp = '/agroseek/www/wp-includes/task_scheduler/task_list' + str(ts)

    with open(task_list_tmp, 'w') as f:
        for task in pending_projects:
            f. write(task + '\n')

    cmd = 'batch < ' + task_list_tmp

    sql = "UPDATE `project_tasks` SET `status` = 'in queue' WHERE task_id in " + f"({','.join(queued_projects)})"
    print(sql)
    cursor.execute(sql)
    connection.commit()

    print(cmd)
    os.system(cmd)
    #os.remove(task_list_tmp)

    connection.close()

    exit()
