#!/bin/bash
cd 'argem_scheduler'

if [ "$#" -ne 5 ]; then
    >&2 echo "wrong number of parameters!"
    >&2 echo "invocation: $0 <metadata file> <project ID> <user ID> <mge database><task_id>"
    exit 2
fi
METADATA=$1
PROJID=$2
USERID=$3
DATABASE=$4
TASKID=$5
python3 -m luigi --module scheduler Runner --metadata $METADATA --proj-ID $PROJID --user-ID $USERID --database $DATABASE --task-ID $TASKID --local-scheduler
