import csv
import json
import sys
import sqldf
import pandas as pd
#Run as python data_process_to_json  <correlation> <output_html file name> <card_database>
if __name__=="__main__":
    correlation = sys.argv[1]
    #spearman = sys.argv[3]
    output = sys.argv[2]
    #print("filtered")
    #print(df)
    nodes = []
    edges = []
    node_names = []
    networkcount = 0
    card_database = sys.argv[3]
    card_type = {}
    with open(card_database, mode='r') as card_file:
       for line in card_file.readlines():
           if len(line.split(',')) < 2:
               continue
           values = line.split(',')
           card_type[values[0]] = values[1]
    #print(card_type)



    with open(correlation, mode='r') as spearman_file:
        #header = spearman_file.readline().split("\n")[0].split(',')
        header = ""
        spearman_reader = csv.reader(spearman_file)
        #print(header)
        for line in spearman_reader:
            if header == "":
                header = line
                continue

            values = line
            target_gene = values[0]
            for i in range(1, len(values)):
                if ('{' in values[i] or values[i] == "" or values[i] == "\n"):
                    continue
                start_gene = header[i]
                if (start_gene == target_gene):
                    continue
                if (start_gene not in node_names):
                    #check if type exists
                    type_gene = ""
                    if start_gene in card_type.keys():
                        type_gene = card_type[start_gene]
                    else:
                        type_gene = "N/A"
                    temp = "{\"data\":{\"id\": \"" + str(int(len(node_names))) + "\", \"idInt\" : " + str(int(len(node_names))) +  ", \"name\": \"" + start_gene + "\", \"label\": \"" + start_gene +  "\", \"query\": false, \"gene\": true, \"type\": \"" + type_gene + "\"}}"
                    node_names.append(start_gene)
                    nodes.append(temp)
                if (target_gene not in node_names):
                    type_gene = ""
                    if target_gene in card_type.keys():
                        type_gene = card_type[target_gene]
                    else:
                        type_gene = "N/A"
                    temp = "{\"data\":{\"id\": \"" + str(int(len(node_names))) + "\", \"idInt\" : " + str(int(len(node_names))) +  ", \"name\": \"" + target_gene + "\", \"label\": \"" + target_gene +  "\", \"query\": false, \"gene\": true, \"type\": \"" + type_gene + "\"}}"
                    node_names.append(target_gene)
                    nodes.append(temp)
                # Remove '\n' at the end of each row
                values[i] = values[i].split('\n')[0]
                # check duplicates 
                if start_gene > target_gene:
                    continue
                temp_edge  = "{\"data\":{\"source\": " + str(int(node_names.index(start_gene))) + ", \"target\" : " + str(int(node_names.index(target_gene))) + ", \"weight\": " + str(abs(float(values[i]))) + ", \"label\": " + str(float(values[i])) + ", \"group\": \"coexp\", \"networkId\": " + str(networkcount) + ", \"networkGroupID\":  18, \"intn\": true, \"rIntnId\": 2, \"id\": \"e"  + str(len(edges)) + "\"}, \"position\":  {}, \"group\": \"edges\", \"removed\": false, \"selected\": false, \"selectable\": true, \"locked\": false, \"grabbed\": false, \"grabbable\": true, \"classes\": \"\"}"
                edges.append(temp_edge)
                networkcount += 1 
                    #    "removed": False,
                    #    "selected": False,
                    #    "selectable": True,
                    #    "locked": False,
                    #    "grabbed": False,
                    #    "grabbable": True,
                    #    "classes": ""
                    #}


    string_nodes = ",\n".join(nodes)
    string_edges = ",\n".join(edges)
    data =  "{\"nodes\": [" + string_nodes + "], \"edges\":[" + string_edges + "]}" 
    #data = "{\"nodes\": [" + string_nodes + "]}"
    #print(data)
    with open(output, 'w') as f:
        f.write("""<!DOCTYPE>

<html>

<head>
    <title>cytoscape correlation demo</title>
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
    "background-color": "#68023F"
    ,'border-color': '#594D5B'
  }
}, {
  "selector": "node[type=\\"aminoglycoside\\"]",
  "style": {
    "background-color": "#008169"
    ,'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"beta-lactam\\"]",
  "style": {
    "background-color": "#EF0096",
    'border-color': '#594D5B'
  }
}, {
  "selector": "node[type=\\"elfamycin\\"]",
  "style": {
    "background-color": "00DCB5",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"fosfomycin\\"]",
  "style": {
    "background-color": "#FFCFE2",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"glycopeptide\\"]",
  "style": {
    "background-color": "#003C86",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"mls\\"]",
  "style": {
    "background-color": "#9400E6",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"multidrug\\"]",
  "style": {
    "background-color": "#009FFA",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"peptide\\"]",
  "style": {
    "background-color": "#FF71FD",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"phenicol\\"]",
  "style": {
    "background-color": "#7CFFFA",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"quinolone\\"]",
  "style": {
    "background-color": "#6A0213",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"rifampin\\"]",
  "style": {
    "background-color": "#008607",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"rifamycin\\"]",
  "style": {
    "background-color": "#F60239",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"sulfonamide\\"]",
  "style": {
    "background-color": "#00E307",'border-color': '#594D5B'

  }
}, {
  "selector": "node[type=\\"tetracycline\\"]",
  "style": {
    "background-color": "#FFDC3D",'border-color': '#594D5B'

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
      alert('correlation: \\n' + ele.data("label"));
 });


       });
    </script>
</body>
</html>




""")





