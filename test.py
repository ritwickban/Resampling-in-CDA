import sys
import os
import pandas as pd
import jpype
import numpy as np
import jpype.imports
import time
import re
import pickle

try :
	jpype.startJVM("-Xmx16g",classpath="tetrad-current.jar")
	print("JVM Started")
except OSError:
	print("JVM already running")

import java.util as util
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.stat.correlation as tsc

def df_to_data(df):
    cols = df.columns
    values = df.values
    n, d = df.shape

    variables = util.ArrayList()
    for col in cols:
        variables.add(td.ContinuousVariable(str(col)))

    databox = td.DoubleDataBox(n, d)

    for col, var in enumerate(values.T):
        for row, val in enumerate(var):
            databox.set(row, col, val)

    return td.BoxDataSet(databox, variables)

def multi_boss(score, discount=[2], starts=1, threads=1):
    
    score.setStructurePrior(0)
    order = None
    bics = []
    times = []

    
    score.setPenaltyDiscount(discount)
        
    boss = ts.Boss(score)
    boss.setUseBes(False)

    boss.setResetAfterBM(True)
    boss.setResetAfterRS(False)

    boss.setUseDataOrder(order != None)
    boss.setNumStarts(starts)
    if starts > 1: starts = 1

    boss.setNumThreads(threads)
    boss.setVerbose(False)

    search = ts.PermutationSearch(boss)
    if order != None: search.setOrder(order)

    graph = search.search()
    order = search.getOrder()
    bics += [bic for bic in boss.getBics()]
    times += [time for time in boss.getTimes()]

    return graph, bics, times

def fges(score, discount=[2], starts=1, threads=1):
    
    score.setStructurePrior(0)
    order = None
    bics = []
    times = []

    
    score.setPenaltyDiscount(discount)
        
    fges = ts.Fges(score)
    fges.setFaithfulnessAssumed(False)
    fges.setNumThreads(threads)
    fges.setVerbose(False)
    graph = fges.search()
    return graph

def sample_90(filepath):
    """Sample 90% of the data."""
    try:
            df = pd.read_csv(filepath)
            samdf = df.sample(frac=0.9, random_state=100)
            
            return samdf, None, '90'
    except Exception as e:
            print(f"Error processing {filepath} for type '90': {e}")
            return None

def Compute(df, ESS=None): 
    data = df_to_data(df) 
    #score.setStructurePrior(0)
    rcm = tsc.RealCovarianceMatrix(data.getDoubleData().toArray())
    cov = td.CovarianceMatrix(data.getVariables(), rcm.compute(True), data.getNumRows())
    if ESS is not None:
        cov.setSampleSize(int(ESS))
    score = ts.score.SemBicScore(cov)
    graph = fges(score, discount=2, threads=1, starts=1)
    return graph

def analyse_graphs(graphs_90,reps=5):
    probs = {}
    for graph in graphs_90:
        edges = [
            edge.split()[1:]
            for edge in graph.split('\n\n')[1].split("Graph Edges:\n")[1].split("\n")
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
                
                if key not in probs: probs[key] = {} #"<--": 0, "-->": 0, "---": 0

                if key[1] in parents[key[0]] and "<--" not in probs[key]: probs[key]["<--"] = 0
                if key[1] in children[key[0]] and "-->" not in probs[key]: probs[key]["-->"] = 0
                if key[1] in neighbors[key[0]] and "---" not in probs[key]: probs[key]["---"] = 0

                if key[1] in parents[key[0]]: probs[key]["<--"] += 1.0 / reps
                if key[1] in children[key[0]]: probs[key]["-->"] += 1.0 / reps
                if key[1] in neighbors[key[0]]: probs[key]["---"] += 1.0 / reps
    
    return probs 


file_path='Data/SF/Variable_20/AD_2/n_40/Sample_1.csv'
start=time.time()
if file_path.endswith(".csv"):

    base=os.path.dirname(file_path)

    types=['90','50','100SS','100ESS','Split']
    for type in types:
        if type=='90':
            graphs_90=[]
            edges_90=[]
            
            for i in range(5):
                result_90=sample_90(file_path)
                df_90,_,type=result_90
                graph=Compute(df_90)
                f=graph.toString()
                graphs_90.append(str(f))
            with open('graphs_90.pkl','wb') as file:
                pickle.dump(graphs_90,file)
                print("Graphs saved")

            
            
with open('graphs_90.pkl','rb') as file:
    graphs_90=pickle.load(file)
    probs=analyse_graphs(graphs_90)
    print(probs)
    for graph in graphs_90:
        edges = [
            edge.split()[1:]
            for edge in graph.split('\n\n')[1].split("Graph Edges:\n")[1].split("\n")
            if edge.strip()
        ]
        print("\n",edges)

            

            
             
