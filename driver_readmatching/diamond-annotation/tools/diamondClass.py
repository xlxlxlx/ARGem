import os
import sys
import pandas as pd
def dsize(dbdata):
    return {i.split()[0].split("|")[-3]: i.split() for i in open(dbdata+".len")}

class diamondpipe():
    def __init__(self, dbpath="/agroseek/www/wp-content/themes/twentyseventeen/scripts/diamond_pipeline/diamond-annotation/bin/"):
        self.info = ""
        #self.argdb = dbdata + 'arg/dataset'
        #self.mrgdb = dbdata + 'mrg/dataset'
        self.dbpath = dbpath
        print(sys.path)
        
    def run(self,fi,data):
        dbpart=str(data['database'])
        db= self.dbpath+ dbpart + '/dataset'
        
        try:
            cmd = " ".join(
                ['diamond',
                 'blastx',
                 '-e',str(data['evalue']),
                 '--id',str(data['identity']),
                 '-k 1',
                 '-d', db + '.dmnd',
                 '-q', fi,
                 '-a', fi + '.{}'.format(dbpart)
                 ])
            print(cmd)
            os.popen(" ".join(
                ['diamond',
                 'blastx',
                 '-e',str(data['evalue']),
                 '--id',str(data['identity']),
                 '-k 1',
                 '-d', db + '.dmnd',
                 '-q', fi,
                 '-a', fi + '.{}'.format(dbpart)
                 ])).read()
            os.popen(" ".join(
                    ['diamond view',
                     '-a',fi+'.{}.daa'.format(dbpart),
                     '-o', fi + '.{}.matches'.format(dbpart),
                     '-f tab'
                     ])).read()
            genes={}
            
            file=pd.read_csv(fi+'.{}.matches'.format(dbpart),sep='\t',header=None)
            file.sort_values([0,11],inplace=True,ascending=False)
            file.drop_duplicates(subset=0,keep='first',inplace=True)
            file.to_csv(fi+'.{}.matches'.format(dbpart),sep='\t',index=False,header=None)
            
            for lines in open(fi+'.{}.matches'.format(dbpart)):
                i=(lines.strip().split())
                try:
                    if float(i[2])>=float(data['identity']) and int(i[3])>=int(data['mlen']) and float(i[10])<=float(data['evalue']):
                        g=i[1].split('|')
                        genes[g[-3]]['count']+=1
                        genes[g[-3]]['length']+=int(i[3])
                        genes[g[-3]]['type'] = g[-2]
                                    
                except:
                    if float(i[2])>=float(data['identity']) and int(i[3])>=int(data['mlen']) and float(i[10])<=float(data['evalue']):
                        g=i[1].split('|')
                        genes[g[-3]]={'count':1,
                             'length':int(i[3]),
                             'type':g[-2]}
            gene_len = dsize(db)
            print(genes)
            fo = open(fi+".{}.matches.quant".format(dbpart), 'w')
            for gene in genes:
                print(gene, gene_len[gene][1])
                cov = genes[gene]['length']/float(gene_len[gene][1])
                fo.write("\t".join([
                    gene,
                    str(genes[gene]['type']),
                    str(genes[gene]['count']),
                    str(genes[gene]['length']),
                    gene_len[gene][1],
                    str(round(cov, 3))
                ])+"\n")
            fo.close()
            return True
        except:
            return False
