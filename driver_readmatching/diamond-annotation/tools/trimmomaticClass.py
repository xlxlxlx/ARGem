import os
import sys


def pairedEnd(location, R1, R2):
    print(sys.path)
    try:
        os.popen(" ".join(
            ['java -jar ',
             location+'/Trimmomatic-0.36/trimmomatic-0.36.jar PE ',
             R1,
             R2,
             R1+'.paired',
             R1+'.unpaired',
             R2+'.paired',
             R2+'.unpaired',
             'ILLUMINACLIP:'+location+'/Trimmomatic-0.36/adapters/TruSeq3-PE.fa:2:30:10',
             'LEADING:3',
             'TRAILING:3',
             'SLIDINGWINDOW:4:15',
             'MINLEN:36'
             ])).read()
        return True
    except:
        return False
