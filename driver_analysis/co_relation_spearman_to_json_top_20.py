import csv

with open('/agroseek/cytoscape/data_process_to_json/CARD_classification_id.csv', mode='r') as CARD_file:
    reader = csv.reader(CARD_file)
    CARD_type_dict = {}
    CARD_id_dict   = {}

    for rows in reader:
        CARD_type_dict[rows[0]] = rows[1]
        CARD_id_dict[rows[0]]   = rows[2]

with open('/agroseek/cytoscape/data_process_to_json/agroseek_lauren_16S.csv', mode='r') as abundance_sample_file:
    reader = csv.reader(abundance_sample_file)
    list_of_genes = []
    abundance_dict = {}
    sample_dict = {}
    for row in reader:
        list_of_genes.append(row)
        break
    list_of_genes = list_of_genes[0]
    for row in reader:
        index = 0
        sample_name = True
        for sample_abun in row:  
            #if the value is not 0 or empty '' 
            if sample_abun != '' and not sample_name:
                if sample_dict.get(list_of_genes[index], 0) == 0:
                    sample_dict[list_of_genes[index]] = [row[0]]
                    #print sample_dict[list_of_genes[index]]
                    abundance_dict[list_of_genes[index]] = float(sample_abun)
                #print row[0]
                #print sample_dict[list_of_genes[index]]
                else:
                    temp = sample_dict[list_of_genes[index]]
                    temp.append(row[0])
                    sample_dict[list_of_genes[index]] = temp
                    abundance_dict[list_of_genes[index]] += float(sample_abun) 
            sample_name = False
            index += 1
import operator
sorted_abun = sorted(abundance_dict.items(), key=operator.itemgetter(1), reverse = True)
sorted_abun_gene_20 = []
for (gene, abun) in sorted_abun[:20]:
    sorted_abun_gene_20.append(gene)
import json   

data = []
#Create json file
for (gene, abun) in sorted_abun[:20]: 
    if CARD_id_dict.get(gene, 0) == 0:
        CARD_id_dict[gene] = str(int(len(CARD_id_dict)) + 1)
        #TODO how to classify
        CARD_type_dict[gene] = "unknown"
    temp = {
      "data":{
          "id": CARD_id_dict[gene],
          "idInt": int(CARD_id_dict[gene]),
          "name": gene,
          "score": abundance_dict[gene],
          "query": False,
          "gene": True,
          "type": CARD_type_dict[gene], 
          "samples": sample_dict[gene]
      },
      "position": {}
    }
    data.append(json.dumps(temp))

#Spearman 
with open('Spearman_agroseek_lauren_16S_matrix.csv', mode='r') as spearman_file:
    # Each cell is the edge
    spearman_gene_list = []
    reader = csv.reader(spearman_file)
    edge_count = 0
    for row in reader:
        spearman_gene_list.append(row)
        break
    spearman_gene_list = spearman_gene_list[0]
    for row in reader:
        index = 0
        sample_name = True
        for correlation in row:
            #if the value is not 0 or empty '' 
            if (spearman_gene_list[index] in sorted_abun_gene_20 and row[0] in sorted_abun_gene_20) and correlation != '' and not sample_name and index > spearman_gene_list.index(row[0]):
                #create edge 
                common_samples = list((set(sample_dict[spearman_gene_list[index]])).intersection(set(sample_dict[row[0]])))
                temp = {
                    "data":{
                        "source": int(CARD_id_dict[spearman_gene_list[index]]),
                        "target": int(CARD_id_dict[row[0]]),
                        "weight": abs(float(correlation)),
                        "group": "coexp",
                        "networkId": 1133,
                        "networkGroupID": 18,
                        "intn": True,
                        "rIntnId":2, 
                        "id": "e" + str(edge_count),
                        "samples": common_samples
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
                data.append(json.dumps(temp))
                edge_count += 1


                
            
            sample_name = False
            index += 1 
print(data)
with open('co-relation_top_20.json', 'w') as f:
    json.dump(data, f)


