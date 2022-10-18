import pandas as pd
import os

def normalize(fi16s, fiArg, covi, parameters={}):
    N16s = sum([int(i.split()[1])
                for i in open(fi16s) if float(i.split()[2]) >= parameters['identity_16s_alignment']])
    print( "Total number of 16S Reads in the sample: {}".format(N16s) )
    L16s = 1432
    

    LrpoB = 1273

    identity_rpoB = 60
    file_rpoB = ''

    rpoB_db = ''
    input_sequence = '' 
    #rpoB_cmd = f'diamond blastx -d {rpoB_db} --query {input_sequence} --out {file_rpoB} --evalue 1e-5 --max-target-seqs 1'
    # os.system(rpoB_cmd)

    #NrpoB =  sum([int(i.split()[1])
    #            for i in open(file_rpoB) if float(i.split()[2]) >= identity_rpoB])

    ARG_file = pd.read_csv(fiArg, sep = "\t",header=None)
    ARG_file.columns=['gene','type','count','align-len','gene-len','cov']
    
    ARG_file['gene-len(bp)'] = (ARG_file['gene-len']+1)*3
    #print(ARG_file)
    #TPM
    ARG_file['TPM_counts'] = ARG_file['count']/ARG_file['gene-len(bp)']
    ARG_file['TPM_Normalization'] = ARG_file['TPM_counts']/ARG_file['TPM_counts'].sum()
    ARG_file['TPM_Normalization'] = ARG_file['TPM_Normalization'].multiply(1000000)
    
    #FPKM
    ARG_file['FPKM_Normalization'] = (ARG_file['count']/ARG_file['count'].sum())/ARG_file['gene-len(bp)']
    ARG_file['FPKM_Normalization'] = ARG_file['FPKM_Normalization'].multiply(1000000000)
    
    #16S & rpoB
    #L16S = 1432
    #ARG_file['rpoB_Normalization'] = (ARG_file['count']/ARG_file['gene-len(bp)'])/(NrpoB/LrpoB)
    ARG_file['16S_Normalization'] = (ARG_file['count']/ARG_file['gene-len(bp)'])/(N16s/L16s)
    ARG_file=ARG_file[['gene','type','count','TPM_Normalization','FPKM_Normalization','16S_Normalization']]#,'rpoB_Normalization']]
    ARG_file.to_csv(fiArg+'.normalization')
    #print(ARG_file)
    return True
