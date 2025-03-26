import sys
import os
import pickle

# Command-line arguments: pd is the pattern for filenames, reps is the repetitions count.
#pd, reps = [int(x) for x in sys.argv[1:3]]
def process_directory(path, reps,temp,resample):
    #print(path)
    #quit()
    files = os.listdir(path)
    #print(files)
    #quit()
    for file in files:
        #print(file)
        if file.endswith(".pkl"):
            file_path = os.path.join(path, file)
            #print(f"Processing file: {file}")
            probs=analyse_graphs(file_path, reps)
            #print(file.split('_90',)[0])

            # print(probs)
            # quit()
        
    
            # print(files)
            # quit()
            # for file in files:
            #     print(file, f"Sample_{pd}_{resample}")
            #     if file.startswith(f"Sample_{pd}_{resample}") and file.endswith(".pkl"):
            #         file_path = os.path.join(path, file)
            #         print(f"Processing file: {file}")
                    #analyse_graphs(file_path, reps,probs)
            
            # break
            # Save the results
            # output_file = os.path.join(root, f"Analysed")
            # os.makedirs(output_file,exist_ok=True)
            # with open(f'{output_file}/BOSS_analyzed_{pd}.p', "wb") as f:
            #     pickle.dump(probs, f)
            # print(f"Saved probabilities to {output_file}")
            # break
        sample = file.split('Sample_')[1].split('_')[0]
        # print(sample)
        # print('\n')
        # print(probs)
        # print('\n')
        output_file = os.path.join(temp)
        os.makedirs(output_file,exist_ok=True)
        with open(f'{output_file}/FGES_analyzed_{sample}.pkl', "wb") as f:
            pickle.dump(probs, f)
    # #print(f"Saved probabilities to {output_file}")

def analyse_graphs(filepath,reps):
    probs = {}
    with open(filepath, 'rb') as f:
        graphs = pickle.load(f)
    for graph in graphs:
        # if (filepath=='Data/ER/Variable_20/AD_2/n_40/Learnt_graphs_BOSS/90/Sample_51_90_all_graphs.pkl'):
        #     print(graph)
        edges = [
            edge.split()[1:]
            for edge in graph.split('\n\n')[1].replace('Graph Edges:\n','Graph Edges:').split("Graph Edges:")[1].split("\n")
            if edge.strip()
        ]
        # if (filepath=='Data/ER/Variable_20/AD_2/n_40/Learnt_graphs_BOSS/90/Sample_51_90_all_graphs.pkl'):
        #     print(edges)
        # Dictionaries to hold relationships and probabilities
        parents, children, neighbors, nodes = {}, {}, {}, []
        for edge in edges:
            node1, relation, node2 = edge[0], edge[1], edge[2]
            for node in [node1, node2]:
                if node not in parents: parents[node] = []
                if node not in children: children[node] = []
                if node not in neighbors: neighbors[node] = []
                if node not in nodes: nodes.append(node)

            if relation == "-->":
                parents[node2].append(node1)
                children[node1].append(node2)
            elif relation == "<--":
                parents[node1].append(node2)
                children[node2].append(node1)
            elif relation == "---":
                neighbors[node1].append(node2)
                neighbors[node2].append(node1)
            
        # Compute probabilities
        nodes.sort()
        for i in range(len(nodes)):
            for j in range(i):
                key = (nodes[i], nodes[j])
                if key[0] not in parents and key[0] not in children and key[0] not in neighbors:
                    continue
                if key[1] not in parents[key[0]] and key[1] not in children[key[0]] and key[1] not in neighbors[key[0]]:
                    continue
                
                if key not in probs: probs[key] = {} #"<--": 0, "-->": 0, "---": 0

                if key[0] in parents[key[1]] and "-->" not in probs[key]: probs[key]["-->"] = 0
                if key[0] in children[key[1]] and "<--" not in probs[key]: probs[key]["<--"] = 0
                if key[0] in neighbors[key[1]] and "---" not in probs[key]: probs[key]["---"] = 0

                if key[0] in parents[key[1]]: probs[key]["-->"] += 1.0 / reps
                if key[0] in children[key[1]]: probs[key]["<--"] += 1.0 / reps
                if key[0] in neighbors[key[1]]: probs[key]["---"] += 1.0 / reps
    return probs

# def process_graph(file_path, reps, probs):
#     with open(file_path, 'r') as f:
#         edges = [
#             edge.split()[1:]
#             for edge in f.read().split('\n\n')[1].split("Graph Edges:\n")[1].split("\n")
#             if edge.strip()
#         ]
    
#     # Dictionaries to hold relationships and probabilities
#     parents, children, neighbors, nodes = {}, {}, {}, []

#     for edge in edges:
#         node1, relation, node2 = edge[0], edge[1], edge[2]
#         for node in [node1, node2]:
#             if node not in parents: parents[node] = []
#             if node not in children: children[node] = []
#             if node not in neighbors: neighbors[node] = []
#             if node not in nodes: nodes.append(node)

#         if relation == "-->":
#             parents[node2].append(node1)
#             children[node1].append(node2)
#         elif relation == "<--":
#             parents[node1].append(node2)
#             children[node2].append(node1)
#         elif relation == "---":
#             neighbors[node1].append(node2)
#             neighbors[node2].append(node1)

#     # Compute probabilities

#     nodes.sort()
#     for i in range(len(nodes)):
#         for j in range(i):
#             key = (nodes[i], nodes[j])
#             if key[0] not in parents and key[0] not in children and key[0] not in neighbors:
#                 continue
#             if key[1] not in parents[key[0]] and key[1] not in children[key[0]] and key[1] not in neighbors[key[0]]:
#                 continue
            
#             if key not in probs: probs[key] = {"<--": 0, "-->": 0, "---": 0}

#             # if ((key[1] in parents[key[0]]) & ("<--" not in probs[key])): probs[key].setdefault("<--", 0)
#             # if key[1] in children[key[0]]: probs[key].setdefault("-->", 0)
#             # if key[1] in neighbors[key[0]]: probs[key].setdefault("---", 0)

#             if key[1] in parents[key[0]]: probs[key]["<--"] += 1.0 / reps
#             if key[1] in children[key[0]]: probs[key]["-->"] += 1.0 / reps
#             if key[1] in neighbors[key[0]]: probs[key]["---"] += 1.0 / reps
reps=1
variables = [20,100]
avg_deg = [2,6]
sample_sizes = [40, 80, 160, 320, 640, 1280, 2560, 5120, 10240]
#sample_sizes = [40]
st_type = ['ER', 'SF']
resamples=['None_PD1','None_PD2']
for st in st_type:
    for p in variables:
        for ad in avg_deg:
            for sample in sample_sizes:
                #if (p==20) and (int(sample)==40): continue
                print(st,ad,p,sample)
                print('\n')
                for resample in resamples:
                    if (p==100) and (int(sample)<320): continue
                    base_path = f"Data/{st}/Variable_{p}/AD_{ad}/n_{sample}/No_resam_FGES/{resample}/"  # Base directory containing all subdirectories.
                    temp=base_path.replace('Data','No_resam_FGES')
                    # if p == 20:
                    #     num_graphs = 250
                    # else:
                    #     num_graphs = 50
                    #for pd in range(num_graphs):
                        #process_directory(base_path, pd, reps,temp,resample)
                        #print(base_path)
                        #quit()
                        #process_directory(base_path, pd+1, reps,temp,resample)
                    process_directory(base_path,reps,temp,resample)

#path =f"analysed/{type}/Variable{}"

#Analysed_BOSS/ER/Variable_20/AD_2/n_40/Learnt_graphs_BOSS/90/