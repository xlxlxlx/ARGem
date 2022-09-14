
import pandas as pd
import sys
import os.path

join_method = 'outer'
df_project_filename = 'combined.clean.card.matches.quant.normalization'

#filepath = '/agroseek/www/wp-includes/task_scheduler/userprojects/project_5f707efa8c1d7_1654099049/shortreads_output/'

if len(sys.argv) > 1:
    filepath = sys.argv[1]

df_project_16S = pd.DataFrame()
df_project_TPM = pd.DataFrame()
df_project_FPKM = pd.DataFrame()

for fn in os.listdir(filepath):
    with open(filepath + fn, "r+") as f:
        if not fn.endswith('clean.card.matches.quant.normalization'):
            continue
        print(fn)
        df_sample = pd.read_csv(f, index_col=0)
        df_sample = df_sample.T
        df_sample.columns = df_sample.iloc[0]
        #df_sample = df_sample.iloc[1:, :]
        df_sample.index = [fn.split('.')[0]]*6
        print(df_sample)
        df_sample_TPM = pd.DataFrame(df_sample.iloc[3, :]).T
        df_sample_FPKM = pd.DataFrame(df_sample.iloc[4, :]).T
        df_sample_16S = pd.DataFrame(df_sample.iloc[5, :]).T
        df_project_16S = pd.concat([df_project_16S, df_sample_16S], axis=0, join=join_method, sort=False)
        df_project_TPM = pd.concat([df_project_TPM, df_sample_TPM], axis=0, join=join_method, sort=False)
        df_project_FPKM  = pd.concat([df_project_FPKM, df_sample_FPKM], axis=0, join=join_method, sort=False)


# if df_project.empty():
#  exit("This project contains no annotations")
df_project_16S.insert(0, 'Label','default')
df_project_TPM.insert(0, 'Label','default')
df_project_FPKM.insert(0, 'Label','default')
df_project_16S.to_csv(filepath + df_project_filename + '.16S.csv', index_label='sample_id')
df_project_TPM.to_csv(filepath + df_project_filename + '.TPM.csv', index_label='sample_id')
df_project_FPKM.to_csv(filepath + df_project_filename + '.FPKM.csv', index_label='sample_id')

# print('project_' + project_id + df_group_file_name)
print(df_project_filename)
# return df_group_file_list

