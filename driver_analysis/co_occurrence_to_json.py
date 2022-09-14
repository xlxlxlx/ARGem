import csv
import json
import sys
import sqldf
import pandas as pd
#Run as python data_process_to_json <CARD> <occurrence> <output_json file name> <treshhold>
if __name__=="__main__":
    CARD = sys.argv[1]
    occurrence = sys.argv[2]
    #spearman = sys.argv[3]
    output = sys.argv[3]
    threshold = 0
    if len(sys.argv) > 4:
        threshold = int(sys.argv[4])
    
    with open(CARD, mode='r') as CARD_file:
        reader = csv.reader(CARD_file)
        CARD_type_dict = {}
        CARD_id_dict   = {}

        for rows in reader:
            #print(rows)
            CARD_type_dict[rows[0]] = rows[1]
            CARD_id_dict[rows[0]]   = rows[2]
    list_of_ARG = {}
    list_of_MGE = {}
    nodes = []
    edges = []
    iter_csv = pd.read_csv(occurrence, iterator=True, sep='\t', header=0)
    df = pd.concat([occurrence[occurrence['count'].astype(int) > threshold] for occurrence in iter_csv])
    #print("filtered")
    #print(df)
    for i in range(0,df.shape[0]):
        arg_line = str(df.iloc[i]['ARG'])
        mge_line = str(df.iloc[i]['MGE'])
        count = int(df.iloc[i]['count'])
        
        if count > threshold:   
           if arg_line not in list_of_ARG.keys():
                list_of_ARG[arg_line] = len(nodes) + 1
                # add to node
                if arg_line.split('|')[3] not in CARD_type_dict.keys(): 
                    card_type_line = "N/A"
                else:
                    card_type_line = CARD_type_dict[arg_line.split('|')[3]] 
                temp = {
                  "data":{
                      "id": list_of_ARG[arg_line],
                      "idInt": int(list_of_ARG[arg_line]),
                      "name": arg_line,
                      #"score": abundance_dict[gene]],
                      "query": False,
                      "gene": True,
                      "type": card_type_line,
                      #"samples": sample_dict[gene]
                    },
                    "position": {}
                  }
                nodes.append(json.dumps(temp))
           if mge_line not in list_of_MGE.keys():
               list_of_MGE[mge_line] = len(nodes) + 1
               # add to node
               temp = {
                  "data":{
                      "id": list_of_MGE[mge_line],
                      "idInt": int(list_of_MGE[mge_line]),
                      "name": mge_line,
                      #"score": abundance_dict[gene]],
                      "query": False,
                      "gene": True,
                      #"type": CARD_type_dict[arg_line],
                      #"samples": sample_dict[gene]
                    },
                    "position": {}
                  }
               nodes.append(json.dumps(temp))
             
           # Create edge between two 
           temp_edge  = {
                        "data":{
                            "source": int(list_of_ARG[arg_line]),
                            "target": int(list_of_MGE[mge_line]),
                            "weight": count,
                            "group": "coexp",
                            "networkId": 1133,
                            "networkGroupID": 18,
                            "intn": True,
                            "rIntnId":2,
                            "id": "e" + str(len(edges)),
                            #"samples": common_samples
                       },
                       "position": {},
                        "group": "edges",
                        "removed": False,
                        "selected": False,
                        "selectable": True,
                        "locked": False,
                        "grabbed": False,
                        "grabbable": True,
                        "classes": ""
                    }
           edges.append(json.dumps(temp_edge))





#        list_of_genes = []
#        abundance_dict = {}
#        sample_dict = {}
#        for row in reader:
#            list_of_genes.append(row)
#            break
#        list_of_genes = list_of_genes[0]
#        for row in reader:
#            index = 0
#            sample_name = True
#            for sample_abun in row:  
#                #if the value is not 0 or empty '' 
#                if sample_abun != '' and not sample_name:
#                    if sample_dict.get(list_of_genes[index], 0) == 0:
#                        sample_dict[list_of_genes[index]] = [row[0]]
#                        #print sample_dict[list_of_genes[index]]
#                        abundance_dict[list_of_genes[index]] = float(sample_abun)
#                #print row[0]
#                #print sample_dict[list_of_genes[index]]
#                    else:
#                        temp = sample_dict[list_of_genes[index]]
#                        temp.append(row[0])
#                        sample_dict[list_of_genes[index]] = temp
#                        abundance_dict[list_of_genes[index]] += float(sample_abun) 
#                sample_name = False
#                index += 1


#import json   

#    nodes = []
    #Create json file
#    for gene in list_of_genes[1:]: 
#        if CARD_id_dict.get(gene, 0) == 0:
#            CARD_id_dict[gene] = str(int(len(CARD_id_dict)) + 1)
#            #TODO how to classify
#            CARD_type_dict[gene] = "unknown"
#        temp = {
#          "data":{
#              "id": CARD_id_dict[gene],
#              "idInt": int(CARD_id_dict[gene]),
#              "name": gene,
#              "score": abundance_dict[gene],
#              "query": False,
#              "gene": True,
#              "type": CARD_type_dict[gene], 
#              "samples": sample_dict[gene]
#          },
#          "position": {}
#        }
#        nodes.append(json.dumps(temp))
#    edges=[]
#    #Spearman 
#    with open(spearman, mode='r') as spearman_file:
#        # Each cell is the edge
#        spearman_gene_list = []
#        reader = csv.reader(spearman_file)
#        edge_count = 0
#        for row in reader:
#            spearman_gene_list.append(row)
#            break
#        spearman_gene_list = spearman_gene_list[0]
#        for row in reader:
#            index = 0
#            sample_name = True
#            for correlation in row:
#                #if the value is not 0 or empty '' 
#                if correlation != '' and not sample_name and index > spearman_gene_list.index(row[0]):
#                    #create edge 
#                    common_samples = list((set(sample_dict[spearman_gene_list[index]])).intersection(set(sample_dict[row[0]])))
#                    temp = {
#                        "data":{
#                            "source": int(CARD_id_dict[spearman_gene_list[index]]),
#                            "target": int(CARD_id_dict[row[0]]),
#                            "weight": abs(float(correlation)),
#                            "group": "coexp",
#                            "networkId": 1133,
#                            "networkGroupID": 18,
#                            "intn": True,
#                            "rIntnId":2, 
#                            "id": "e" + str(edge_count),
#                            "samples": common_samples
#                       }, 
#                       "position": {}, 
#                        "group": "edges",
#                        "removed": False,  
#                        "selected": False, 
#                        "selectable": True,  
#                        "locked": False, 
#                        "grabbed": False,  
#                        "grabbable": True, 
#                        "classes": ""
#                    }
#                    edges.append(json.dumps(temp))


                
            
#                sample_name = False
#                index += 1

    data = {'elements' : [ {'nodes': nodes}, {'edges': edges} ]} 
    print(data)
    with open(output, 'w') as f:
        json.dump(data, f)


