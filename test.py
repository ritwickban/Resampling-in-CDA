import sys
import os
import pandas as pd
import jpype
import numpy as np
import jpype.imports
import time
import re
import pickle
from visualize import graphs_to_probs

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

    boss.setResetAfterBM(False)
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
    sum_bic = sum(bics)
    print(str(sum_bic))
    #print(str(bics))
    return graph

def fges(score, discount=2, starts=1, threads=1):
    
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
    print(str(fges.getModelScore()))
    return graph

def run_pc(cov, alpha=0.01, pc_depth=-1):
    
    alpha = 0.01
    pc_depth=pc_depth
    test = ts.test.IndTestFisherZ(cov, alpha)
    pc = ts.Pc(test)
    pc.setDepth(pc_depth)    
    pc.setStable(True)
    graph = pc.search()

    
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
    
def sample_100ESS(filepath):

    try:
        df = pd.read_csv(filepath)
        rng = np.random.default_rng()
        idxs = rng.choice(len(df), size=len(df), replace=True)
        _, counts = np.unique(idxs, return_counts=True)
        eff_ss = np.sum(counts) ** 2 / np.sum(np.power(counts, 2))
        samdf = pd.DataFrame(df.iloc[idxs, :].values, columns=df.columns)
        return samdf, eff_ss, '100ESS'
    except Exception as e:
        print(f"Error processing {filepath} for type '100ESS': {e}")
        return None



def Compute(df, ESS=None): 
    data = df_to_data(df) 
    #score.setStructurePrior(0)
    rcm = tsc.RealCovarianceMatrix(data.getDoubleData().toArray())
    cov = td.CovarianceMatrix(data.getVariables(), rcm.compute(True), data.getNumRows())
    if ESS is not None:
        cov.setSampleSize(int(ESS))
    # score = ts.score.SemBicScore(cov)
    # score.setUsePseudoInverse(True)
    graph = run_pc(cov, alpha=0.01, pc_depth=100)
    

    #print(f"\n Edges : {int(graph.getNumEdges())}\n")

    return graph


file_path='Data/ER/Variable_100/AD_6/n_10240/Sample_20.csv'
start=time.time()
if file_path.endswith(".csv"):

    base=os.path.dirname(file_path)

    types=['90','50','100SS','100ESS','Split']
    start=time.time()
    for type in types:
        if type=='100SS':
            graphs_90=[]
            edges_90=[]
            
            for i in range(100):
                #print("100SS")
                result_90=sample_100(file_path)
                df_90,_,type=result_90
                graph=Compute(df_90)
                #f=graph.toString()
                #print(f)
                graphs_90.append(graph)
                #graphs_90.append(str(f))
            
            probs=graphs_to_probs(graphs_90)
            print(probs)


            with open('graphs_90.pkl','wb') as file:
                pickle.dump(str(graphs_90),file)
                print("Graphs saved")
            end =time.time()
            print("Time taken: ",end-start)
            quit()

        elif type=='100ESS':
                # Generating 100 samples, running boss, storing graphs
                graphs_100ESS=[]
                for i in range(5):
                    print("100ESS")
                    result_100ESS=sample_100ESS(file_path)
                    df_100ESS,ESS,type=result_100ESS
                    graph=Compute(df_100ESS, ESS)
                    # f=graph.toString()
                    graphs_100ESS.append(graph)
                
                probs1=graphs_to_probs(graphs_100ESS)
                print(probs1)
                with open('graphs_100ESS.pkl','wb') as file:
                    pickle.dump(str(graphs_100ESS),file)
                    print("100ESS done")
    end =time.time()
    print("Time taken: ",end-start)



            
            
# with open('Data/ER/Variable_20/AD_2/n_40/Learnt_graphs_fges/90/Sample_51_90_all_graphs.pkl','rb') as file:
#     graphs_90=pickle.load(file)

    # with open('graphs.txt', 'w') as file:
    #     for graph in graphs_90:
    #         file.write(str(graph) + '\n')
    #print(graphs_90)
    # with open('graphs_90.pkl','rb') as file:
    #     graphs_loaded=pickle.load(file)
    #     print("Graphs loaded")
    # probs=analyse_graphs(graphs_loaded)
    #print(probs)
    # for graph in graphs_90:
    #    print(graph.split('\n\n')[1])
    #print(len(graphs_90))
    # probs={}
    # reps=100
    # for graph in graphs_90:
    #     edges = [
    #         edge.split()[1:]
    #         for edge in graph.split('\n\n')[1].split("Graph Edges:\n")[1].split("\n")
    #         if edge.strip()
    #     ]
    # #    
    # for graph in graphs_90:
    #     temp=graph.split('\n\n')[1]
    #     temp=temp.replace('Graph Edges:\n','Graph Edges:')
    #     print(temp)
    #     temp2=temp.split("Graph Edges:")
    #     print('\n\n')
    #     print(temp2)



            

            
             
