import sys
import os
import pandas as pd
import jpype
import numpy as np
import jpype.imports

try :
	jpype.startJVM("-Xmx16g",classpath="../tetrad-current.jar")
	print("JVM Started")
except OSError:
	print("JVM already running")

import java.util as util
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.search as ts

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

def sample_90(filepath):
    """Sample 90% of the data."""
    try:
            df = pd.read_csv(filepath)
            samdf = df.sample(frac=0.9, random_state=100)
            
            return samdf, None, '90'
    except Exception as e:
            print(f"Error processing {filepath} for type '90': {e}")
            return None

file_path='Data/ER/Variable_20/AD_2/n_40/Sample_1.csv'

for i in range(1,5):
    result_90=sample_90(file_path)
    df_90,_,type=result_90
    data = df_to_data(df_90)
    score = ts.score.SemBicScore(data, True)
    #score.setStructurePrior(0)
    graph, bics, times = multi_boss(score, discount=2,threads=1,starts=1)
    print(graph)
    print(times)
#with open(f"{output_dir}/{filename.replace('.csv','')}{type}_subsample.txt", "w") as fout:
    #fout.write(str(graph.toString()))
    #fout.write(str(times))