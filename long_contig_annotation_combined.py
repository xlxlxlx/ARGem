
import sys
import os

column_names = '\t'.join(["Query ID"," Subject ID"," Percentage of identical matches"," Alignment length"," Number of mismatches"," Number of gap openings"," Start of alignment in query"," End of alignment in query"," Start of alignment in subject"," End of alignment in subject"," Expected value"," Bit score"])

join_method = 'outer'
card_all_filename = 'card_all.tsv'
mge_all_filename = 'mge_all.tsv'


if len(sys.argv) > 1:
    filepath = sys.argv[1]

card_all_f = filepath + '/' + card_all_filename
mge_all_f = filepath + '/' + mge_all_filename
os.system('echo' + ' "' + column_names + '" >' + card_all_f)
os.system('echo' + ' "' + column_names + '" >' + mge_all_f)


for dir in os.listdir(filepath):
    if not dir.startswith('SRR') or not dir.endswith('annotated'):
        continue
    card_f = filepath+'/'+dir+'/out_card.tsv'
    metacompare_f = filepath+'/'+dir+'/out_metacompare.tsv'
    larsson_f = filepath+'/'+dir+'/out_larsson.tsv'
    mobileog_f = filepath+'/'+dir+'/out_mobileog.tsv'
    os.system('cat' + ' ' + card_f + ' >>' + card_all_f)
    if os.path.exists(metacompare_f):
        os.system('cat' + ' ' + metacompare_f + ' >>' + mge_all_f)
    elif os.path.exists(larsson_f):
        os.system('cat' + ' ' + larsson_f + ' >>' + mge_all_f)
    elif os.path.exists(larsson_f):
        os.system('cat' + ' ' + mobileog_f + ' >>' + mge_all_f)


