#! /usr/bin/env python3
import sys
import pymysql
import db_config as config
import os

if __name__ == "__main__":
    with open('read_mail_output.txt','w') as f:
       f.write('triggered!')
    
    db = config.DATABASE
    stdin_file = sys.stdin
    task_flag = False
    num_module = 7

    try:
        connection = pymysql.connect(host=db['host'],
                                     user=db['account'],
                                     password=db['pwd'],
                                     db=db['db_name'])

        cursor = connection.cursor()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


    for line in stdin_file:
        if "task_ID=" in line:
            task_id = "'"+line.split('task_ID=')[1].split(')')[0]+"'"
            print(task_id)
        if task_flag:
            if line.split('* ')[1][0] == str(num_module):
                #f.write('success')
                sql = "UPDATE `project_tasks` SET `status` = 'success' WHERE task_id in " + f"({task_id})"
                print(sql)
                with open('read_mail_output.txt','a') as f:
                    f.write(sql)
                cursor.execute(sql)
                connection.commit()
            elif 'fail' in line:
                #f.write('fail')
                sql = "UPDATE `project_tasks` SET `status` = 'fail' WHERE task_id = " + f"{task_id}"
                #print(sql)
                cursor.execute(sql)
                connection.commit()
            else:
                #f.write('partial')
                sql = "UPDATE `project_tasks` SET `status` = 'partial_success' WHERE task_id = " + f"{task_id}"
                #print(sql)
                cursor.execute(sql)
                connection.commit()
            task_flag = False
        if line.startswith('Scheduled '+num_module' tasks'):
            task_flag = True
            with open('read_mail_output.txt','a') as f:
               f.write('task_flag')
        
        with open('read_mail_output.txt','a') as f:
            f.write(line)


