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
    networkcount= 0
    for i in range(0,df.shape[0]):
        arg_line = str(df.iloc[i]['ARG'])
        mge_line = str(df.iloc[i]['MGE'])
        count = int(df.iloc[i]['count'])
        
        mge_label = ""
        #TODO specify types of MGE database
        if len(mge_line.split("|")) > 3:
            mge_label = mge_line.split("|")[4].split("_")[0]
        elif "_" in mge_line:
            mge_label = mge_line.split("_")[1]
        else:
            mge_label = mge_line
 
        if count > threshold:   
           if arg_line not in list_of_ARG.keys():
                list_of_ARG[arg_line] = len(nodes) + 1
                # add to node
                if arg_line.split('|')[3] not in CARD_type_dict.keys(): 
                    card_type_line = "N/A"
                else:
                    card_type_line = CARD_type_dict[arg_line.split("|")[3]] 
                temp = "{\"data\":{\"id\": " + str( list_of_ARG[arg_line]) + ", \"idInt\" : " + str(int(list_of_ARG[arg_line])) +  ", \"name\": \"" + arg_line + "\", \"label\": \"" + arg_line.split("|")[3] +  "\", \"query\": false, \"gene\": true, \"type\": \"" + card_type_line+ "\"}}"
                      #"samples": sample_dict[gene]
    
                  
                nodes.append(temp)
           if mge_line not in list_of_MGE.keys():
               list_of_MGE[mge_line] = len(nodes) + 1
               # add to node
               temp = "{\"data\": {\"id\": " + str(list_of_MGE[mge_line]) + ", \"idInt\": " + str(int(list_of_MGE[mge_line])) + ", \"name\": \"" + mge_line + "\", \"query\": false, \"gene\": true, \"label\": \"" +  mge_label + "\", \"type\": \"MGE\"}}"
                     
               nodes.append(temp)
             
           # Create edge between two 
           temp_edge  = "{\"data\":{\"source\": " + str(int(list_of_ARG[arg_line])) + ", \"target\" : " + str(int(list_of_MGE[mge_line])) + ", \"weight\": " + str(count) + ", \"group\": \"coexp\", \"networkId\": " + str(networkcount) + ", \"networkGroupID\":  18, \"intn\": true, \"rIntnId\": 2, \"id\": \"e"  + str(len(edges)) + "\"}, \"position\":  {}, \"group\": \"edges\", \"removed\": false, \"selected\": false, \"selectable\": true, \"locked\": false, \"grabbed\": false, \"grabbable\": true, \"classes\": \"\"}"
                    #    "removed": False,
                    #    "selected": False,
                    #    "selectable": True,
                    #    "locked": False,
                    #    "grabbed": False,
                    #    "grabbable": True,
                    #    "classes": ""
                    #}
           edges.append(temp_edge)


    string_nodes = ",\n".join(nodes)
    string_edges = ",\n".join(edges)
    data =  "{\"nodes\": [" + string_nodes + "], \"edges\":[" + string_edges + "]}" 
    #data = "{\"nodes\": [" + string_nodes + "]}"
    #print(data)
    with open(output, 'w') as f:
        f.write("""<!DOCTYPE>

<html>

<head>
    <title>cytoscape co-occurrence demo</title>
    <script src=\"https://unpkg.com/cytoscape/dist/cytoscape.min.js\"></script>
    <meta name=\"viewport\" content=\"width=device-width, user-scalable=no, initial-scale=1, maximum-scale=1\">
    <script src=\"https://unpkg.com/jquery/dist/jquery.min.js\"></script>
    <script src=\"https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.js\"></script>
    

    <!-- for popper handles -->
    <script src=\"https://unpkg.com/@popperjs/core@2\"></script>
    <script src=\"https://unpkg.com/cytoscape-popper@2.0.0/cytoscape-popper.js\"></script>

    <script src=\"https://unpkg.com/webcola/WebCola/cola.min.js\"></script>
    <script src=\"https://requirejs.org/docs/release/2.3.5/minified/require.js\"></script> 
    <script src=\"https://cdnjs.cloudflare.com/ajax/libs/fetch/3.1.0/fetch.min.js\"></script>
    <script src=\"https://unpkg.com/react@18/umd/react.production.min.js\"></script>
</head>

<style>
    body {
        font-family: helvetica neue, helvetica, liberation sans, arial, sans-serif;
        font-size: 14px;
      }

      #cy {
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        right: 0;
        z-index: 999;
      }

      h1 {
        opacity: 0.5;
        font-size: 1em;
        font-weight: bold;
      }

      #buttons {
        position: absolute;
        right: 0;
        top: 0;
        z-index: 99999;
        margin: 1em;
      }

      .popper-handle {
        width: 20px;
        height: 20px;
        background: red;
        border-radius: 20px;
        z-index: 9999;
      }
</style>

<body>
    <div id=\"cy\"></div>
    <script>
document.addEventListener('DOMContentLoaded', function(){
        var cy = cytoscape({
            container: document.getElementById('cy'),
            wheelSensitivity:.1,
            elements:  """)

        f.write(data)
        f.write(""", 
style: [{
  "selector": "core",
  "style": {
    "selection-box-color": "#AAD8FF",
    "selection-box-border-color": "#8BB0D0",
    "selection-box-opacity": "0.5"
  }
}, {
  "selector": "node",
  "style": {
    "width": "mapData(score, 0, 0.006769776522008331, 20, 60)",
    "height": "mapData(score, 0, 0.006769776522008331, 20, 60)",
    "content": "data(label)",
    "font-size": "12px",
    "text-valign": "center",
    "text-halign": "center",
    "background-color": "#555",
    "text-outline-color": "#555",
    "text-outline-width": "2px",
    "color": "#fff",
    "overlay-padding": "6px",
    "z-index": "10"
  }
}, {
  "selector": "node[?attr]",
  "style": {
    "shape": "rectangle",
    "background-color": "#aaa",
    "text-outline-color": "#aaa",
    "width": "16px",
    "height": "16px",
    "font-size": "6px",
    "z-index": "1"
  }
}, {
  "selector": "node[?query]",
  "style": {
    "background-clip": "none",
    "background-fit": "contain"
  }
}, {
  "selector": "node:selected",
  "style": {
    "border-width": "6px",
    "border-color": "#AAD8FF",
    "border-opacity": "0.5",
    "background-color": "#77828C",
    "text-outline-color": "#77828C"
  }
}, {
  "selector": "edge",
  "style": {
    "curve-style": "haystack",
    "haystack-radius": "0.5",
    "opacity": "0.8",
    "line-color": "#bbb",
    "width": "data(weight)", //(weight, 0, 1, 1, 8)",
    "overlay-padding": "3px"
  }
}, {
  "selector": "node.unhighlighted",
  "style": {
    "opacity": "0.2"
  }
}, {
  "selector": "edge.unhighlighted",
  "style": {
    "opacity": "0.05"
  }
}, {
  "selector": ".highlighted",
  "style": {
    "z-index": "999999"
  }
}, {
  "selector": "node.highlighted",
  "style": {
    "border-width": "6px",
    "border-color": "#AAD8FF",
    "border-opacity": "0.5",
    "background-color": "#394855",
    "text-outline-color": "#394855"
  }
}, {
  "selector": "edge.filtered",
  "style": {
    "opacity": "0"
  }
}, {
  "selector": "node[group=\\"coexp\\"]",
  "style": {
    "background-color": "#d0b7d5"
  }
}, {
  "selector": "node[type=\\"aminocoumarin\\"]",
  "style": {
    "background-color": "#CO413B"
    ,'border-color': '#594D5B'
  }
}, {
  "selector": "node[type=\\"aminoglycoside\\"]",
  "style": {
    "background-color": "#D77B5F"
    ,'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"beta-lactam\\"]",
  "style": {
    "background-color": "#FF9200",
    'border-color': '#594D5B'
  }
}, {
  "selector": "node[type=\\"beta-lactam\\"]",
  "style": {
    "background-color": "#FF9200",
    'border-color': '#594D5B'
  }
}, {
  "selector": "node[type=\\"elfamycin\\"]",
  "style": {
    "background-color": "#FFCD73",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"fosfomycin\\"]",
  "style": {
    "background-color": "#F7E5BF",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"glycopeptide\\"]",
  "style": {
    "background-color": "#C87505",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"mls\\"]",
  "style": {
    "background-color": "#C14C32",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"multidrug\\"]",
  "style": {
    "background-color": "#80003A",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"other\\"]",
  "style": {
    "background-color": "#506432",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"peptide\\"]",
  "style": {
    "background-color": "#B30019",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"phenicol\\"]",
  "style": {
    "background-color": "#EC410B",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"quinolone\\"]",
  "style": {
    "background-color": "#FFF7C2",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"rifampin\\"]",
  "style": {
    "background-color": "#FFB27B",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"rifamycin\\"]",
  "style": {
    "background-color": "#BC7576",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"sulfonamide\\"]",
  "style": {
    "background-color": "#696B7E",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"tetracycline\\"]",
  "style": {
    "background-color": "#FFA400",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"MGE\\"]",
  "style" : {
    "shape": "rectangle"
    
      
  }
}   
                ],
              
            layout: {
                name: 'cose',
                idealEdgeLength: 100,
                nodeOverlap: 20,
                refresh: 20,
                fit: true,
                padding: 30,
                randomize: false,
                componentSpacing: 100,
                nodeRepulsion: 400000,
                edgeElasticity: 100,
                nestingFactor: 5,
                gravity: 80,
                numIter: 1000,
                initialTemp: 200,
                coolingFactor: 0.95,
                minTemp: 1.0
           }
    });
 cy.nodes().on('click', function(e){
      var ele = e.target;
      alert('type: '+ ele.data("type") + '\\nname: \\n' + ele.data("name"));
  }); 


 cy.edges().on('click', function(e) {
      var ele = e.target;
      alert('occurrence: \\n' + ele.data("weight"));
 });


       });
    </script>
</body>
</html>


""")

