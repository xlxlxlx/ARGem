import sys
import pandas as pd

input_fn = sys.argv[1]
output_fn = sys.argv[2]
mode = sys.argv[3]


#input_fn = "combinations15.tsv"
#output_fn = "combinations15_filter.tsv"

#input_fn = "correlation15.csv"
#output_fn = "correlation15_filter.csv"

filter_fn = "housekeeping_CARD_list.csv"
filter_df = pd.read_csv(filter_fn)
filter_list = filter_df['Gene'].tolist()
#mode = "correlation"



if mode == "correlation":
    df = pd.read_csv(input_fn, index_col=0)
    df = df.loc[:, ~df.columns.isin(filter_list)]
    df = df.loc[~df.index.isin(filter_list),:]
    df.to_csv(output_fn) 
elif mode == "coocurrence":
    df = pd.read_csv(input_fn, delimiter="\t")
    df['ARG_gene'] = df.iloc[:,0].str.split("|").str[-1]
    df = df[~df['ARG_gene'].isin(filter_list)]
    df.to_csv(output_fn, sep="\t", index=False) 