import sys
import os
import pickle

# Command-line arguments: pd is the pattern for filenames, reps is the repetitions count.
#pd, reps = [int(x) for x in sys.argv[1:3]]
def process_directory(path, pd, reps,temp,resample):
    files = os.listdir(path)
    probs={}
    if len(files)==5000:
        for file in files:
            if file.startswith(f"Sample_{pd}{resample}") and file.endswith(".txt"):
                file_path = os.path.join(path, file)
                #print(f"Processing file: {file}")
                process_graph(file_path, reps,probs)
                
                # break
                # Save the results
                # output_file = os.path.join(root, f"Analysed")
                # os.makedirs(output_file,exist_ok=True)
                # with open(f'{output_file}/Boss_analyzed_{pd}.p', "wb") as f:
                #     pickle.dump(probs, f)
                # print(f"Saved probabilities to {output_file}")
        #print(probs)
        output_file = os.path.join(temp,f"Analysed")
        os.makedirs(output_file,exist_ok=True)
        with open(f'{output_file}/Boss_analyzed_{pd}.p', "wb") as f:
            pickle.dump(probs, f)
        #print(f"Saved probabilities to {output_file}")

def process_graph(file_path, reps, probs):
    with open(file_path, 'r') as f:
        edges = [
            edge.split()[1:]
            for edge in f.read().split("Graph Edges:\n")[1].split("\n")
            if edge.strip()
        ]
    
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
            
            if key not in probs: probs[key] = {}

            if key[0] in parents[key[1]]: probs[key].setdefault("-->", 0)
            if key[0] in children[key[1]]: probs[key].setdefault("<--", 0)
            if key[0] in neighbors[key[1]]: probs[key].setdefault("---", 0)

            if key[0] in parents[key[1]]: probs[key]["-->"] += 1.0 / reps
            if key[0] in children[key[1]]: probs[key]["<--"] += 1.0 / reps
            if key[0] in neighbors[key[1]]: probs[key]["---"] += 1.0 / reps
reps=100
variables = [20,100]
avg_deg = [2,6]
sample_sizes = [40, 80, 160, 320, 640, 1280, 2560, 5120, 10240]
#sample_sizes = [40]
st_type = ['ER', 'SF']
resamples=['90','50','100SS','100ESS']
for st in st_type:
    for p in variables:
        for ad in avg_deg:
            for sample in sample_sizes:
                print(st,ad,p,sample)
                print('\n')
                for resample in resamples:
                    if (p==100) and (int(sample)<320): continue
                    base_path = f"Data/{st}/Variable_{p}/AD_{ad}/n_{sample}/processed_output/{resample}/"  # Base directory containing all subdirectories.
                    temp=base_path.replace('Data','Analysed')
                    for pd in range(1,51):
                        process_directory(base_path, pd, reps,temp,resample)

#path =f"analysed/{type}/Variable{}"