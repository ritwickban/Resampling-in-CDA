from boss import boss
import time
import os
import pickle
import pandas as pd
import numpy as np
import jpype 
import jpype.imports

try :
	jpype.startJVM("-Xmx16g",classpath="tetrad-current.jar")
	print("JVM Started")
except OSError:
	print("JVM already running")

import java.util as util
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.algcomparison as ta


def df_to_data(df):
    cols = df.columns
    values = df.values
    n, p = df.shape

    variables = util.ArrayList()
    for col in cols:
        variables.add(td.ContinuousVariable(str(col)))

    databox = td.DoubleDataBox(n, p)
    for col, var in enumerate(values.T):
        for row, val in enumerate(var):
            databox.set(row, col, val)

    return td.BoxDataSet(databox, variables)


def construct_graph(g, nodes, cpdag=True):
    graph = tg.EdgeListGraph(nodes)

    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if g[i, j]: graph.addDirectedEdge(b, a)

    if cpdag: graph = tg.GraphTransforms.dagToCpdag(graph)

    return graph

def sample_100(filepath):
    """Sample 90% of the data."""
    try:
            df = pd.read_csv(filepath)
            samdf = df.sample(frac=1, replace=True)
            
            return samdf, None, '90'
    except Exception as e:
            print(f"Error processing {filepath} for type '90': {e}")
            return None

def analyse_graphs(graphs_90,reps=10):
    probs = {}
    #print(graphs_90) 
    for graph in graphs_90:
        #print(graph)
        edges = [
            edge.split()[1:]
            for edge in graph.split("\n\n")[1].split("\n")[1:]
            if edge.strip()
        ]
        #print(edges)
        #
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

file_path='Data/SF/Variable_100/AD_6/n_320/Sample_20.csv'
start=time.time()
if file_path.endswith(".csv"):
    df_100, _, _ = sample_100(file_path)
    #df=pd.read_csv(file_path)
    graphs=[]
    for i in range (1):
        R=df_100.corr().astype(np.float32).to_numpy()
        data=df_to_data(df_100)
        dag=boss(R,320,1.0,1)
        nodes = data.getVariables()
        # test = str(construct_graph(dag, nodes).toString())
        # break
        graphs.append(str(construct_graph(dag, nodes).toString()))
        #print(graphs)
    with open('graphs.pkl','wb') as file:
            pickle.dump(graphs,file)
            print("Graphs saved")
    with open('graphs.pkl','rb') as file:
        graphs_loaded=pickle.load(file)
        print("Graphs loaded")
    #print(str(graphs_loaded))
    probs=analyse_graphs(graphs_loaded)
    print(probs)

    # edges = [
    #         edge.split()[1:]
    #         for edge in test.split("\n\n")[1].split("\n")[1:]
    #         if edge.strip()
    #     ]
    # print(edges)


    # lines = test.split("\n\n")[1].split("\n")[1:]
    
    # for line in lines:
    #      if "Graph Edges" in line: continue
    #      if len(line) <= 1: continue
    #      edge = line.split()[1:]
     
    # for edges in test.split('\n')[0]:
    #     print(edges)

    #graphs.append(dag)
