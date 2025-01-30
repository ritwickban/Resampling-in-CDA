import sys
import os
import pandas as pd
import jpype
import numpy as np
import jpype.imports
import pickle
import shutil

try :
	jpype.startJVM("-Xmx16g",classpath="tetrad-current.jar")
	print("JVM Started")
except OSError:
	print("JVM already running")

import java.util as util
import edu.cmu.tetrad.stat.correlation as tsc
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

def sample_90(filepath):
    """Sample 90% of the data."""
    try:
            df = pd.read_csv(filepath)
            samdf = df.sample(frac=0.9)
            
            return samdf, None, '90'
    except Exception as e:
            print(f"Error processing {filepath} for type '90': {e}")
            return None

def sample_50(filepath):
    """Sample 50% of the data."""
    try:
        df = pd.read_csv(filepath)
        samdf = df.sample(frac=0.5)
        return samdf, None, '50'
    except Exception as e:
        print(f"Error processing {filepath} for type '50': {e}")
        return None

def sample_100SS(filepath):
    """Sample 100% of the data with replacement."""
    try:
        df = pd.read_csv(filepath)
        samdf = df.sample(frac=1, replace=True)
        return samdf, None, '100SS'
    except Exception as e:
        print(f"Error processing {filepath} for type '100SS': {e}")
        return None

def sample_100ESS(filepath):
    """Sample 100% of the data with replacement and calculate effective sample size."""
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

def sample_split(filepath):
    """Split the dataset into two halves randomly."""
    try:
        df = pd.read_csv(filepath)
        mask = [True] * (len(df) // 2) + [False] * (len(df) // 2)
        np.random.shuffle(mask)
        h1 = df[mask]
        h2 = df[[not b for b in mask]]
        return h1, h2, 'Split'
    except Exception as e:
        print(f"Error processing {filepath} for type 'Split': {e}")
        return None

def multi_boss(score, discounts=[2], starts=1, threads=1):
    
    score.setStructurePrior(0)
    order = None
    bics = []
    times = []


    score.setPenaltyDiscount(discounts)
        
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

    return graph

# Transforms dataframe to Tetrad dataframe, computes covariance matrix and then scomputes SEMBIC score and runs boss.
def Compute(df, ESS=None): 
    data = df_to_data(df) 
    #score.setStructurePrior(0)
    rcm = tsc.RealCovarianceMatrix(data.getDoubleData().toArray())
    cov = td.CovarianceMatrix(data.getVariables(), rcm.compute(True), data.getNumRows())
    if ESS is not None:
        cov.setSampleSize(int(ESS))
    score = ts.score.SemBicScore(cov)
    graph = multi_boss(score, discounts=2, threads=1, starts=1)
    return graph

def main(folderpath):
    if folderpath.endswith(".csv"):
        base=os.path.dirname(folderpath)
        outputdir=os.path.join(base,"Learnt_graphs_BOSS")
        os.makedirs(outputdir,exist_ok=True)
        types=['90','50','100SS','100ESS','Split']
        for type in types:
            typedir=os.path.join(outputdir,type)
            os.makedirs(typedir,exist_ok=True)
            if type=='90':
                # Generating 100 samples, running boss, storing graphs
                graphs_90=[]
                for i in range(1,101):
                    result_90=sample_90(folderpath)
                    df_90,_,type=result_90
                    graph=Compute(df_90)
                    f=graph.toString()
                    graphs_90.append(str(f))
                    with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                        pickle.dump(graphs_90,fout)
                        print("90 done")
                    # with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_subsample_{i}.txt", "w") as fout:
                    #     fout.write(str(graph.toString()))
            elif type=='50':
                graphs_50=[]
                # Generating 100 samples, running boss, storing graphs
                for i in range(1,101):
                    result_50=sample_50(folderpath)
                    df_50,_,type=result_50
                    graph=Compute(df_50)
                    f=graph.toString()
                    graphs_50.append(str(f))
                    with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                        pickle.dump(graphs_50,fout)
                        print("50 done")
                    # with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_subsample_{i}.txt", "w") as fout:
                    #     fout.write(str(graph.toString()))
            elif type=='100SS':
                # Generating 100 samples, running boss, storing graphs
                graphs_100SS=[]
                for i in range(1,101):
                    result_100=sample_100SS(folderpath)
                    df_100,_,type=result_100
                    graph=Compute(df_100)
                    f=graph.toString()
                    graphs_100SS.append(str(f))
                    with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                        pickle.dump(graphs_100SS,fout)
                        print("100SS done")    
                    # with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_bootstrap(SS)_{i}.txt", "w") as fout:
                    #     fout.write(str(graph.toString()))
            elif type=='100ESS':
                # Generating 100 samples, running boss, storing graphs
                graphs_100ESS=[]
                for i in range(1,101):
                    result_100ESS=sample_100ESS(folderpath)
                    df_100ESS,ESS,type=result_100ESS
                    graph=Compute(df_100ESS, ESS)
                    f=graph.toString()
                    graphs_100ESS.append(str(f))
                    with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                        pickle.dump(graphs_100ESS,fout)
                        print("100ESS done")
                    # with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_bootstrap(ESS)_{i}.txt", "w") as fout:
                    #         fout.write(str(graph.toString()))
            elif type=='Split':
                # Generating 100 samples, running boss, storing graphs
                
                graphs_split=[]
                for i in range (1,101):
                    result_split=sample_split(folderpath)
                    df_split1,df_split2,type=result_split
                    graph1=Compute(df_split1)
                    graph2=Compute(df_split2)
                    f1=graph1.toString()
                    f2=graph2.toString()
                    graphs_split.append(str(f1))
                    graphs_split.append(str(f2))
                    with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                        pickle.dump(graphs_split,fout)
                        print("Split done")

                    # with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_(1)_{i}.txt", "w") as fout1:
                    #     fout1.write(str(graph1.toString()))
                    # with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_(2)_{i}.txt", "w") as fout2:
                    #     fout2.write(str(graph2.toString()))
            else:
                print('Error')
            
                

    else:
        output_dir = os.path.join(folderpath, "processed_output")
        os.makedirs(output_dir, exist_ok=True)
        for filename in os.listdir(folderpath):
            if filename.endswith(".csv"):
                file_path = os.path.join(folderpath, filename)
                types=['90','50','100SS','100ESS','Split']
                for type in types:
                    type_dir=os.path.join(output_dir,type)
                    os.makedirs(type_dir,exist_ok=True)
                    if type=='90':
                        graphs_90=[]
                        # Generating 100 samples, running boss, storing graphs
                        for i in range(1,101):
                            result_90=sample_90(file_path)
                            df_90,_,type=result_90
                            graph=Compute(df_90)
                            f=graph.toString()
                            graphs_90.append(str(f))
                            with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                                pickle.dump(graphs_90,fout)
                                print("90 done")
                            # data = df_to_data(df_90)
                            # score = ts.score.SemBicScore(data, False)
                            # #score.setStructurePrior(0)
                            # graph, bics, times = multi_boss(score, discounts=2,threads=1,starts=1)
                            # with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_subsample_{i}.txt", "w") as fout:
                            #     fout.write(str(graph.toString()))
                            #     #fout.write(str(times))
                    elif type=='50':
                        # Generating 100 samples, running boss, storing graphs
                        graphs_50=[]
                        for i in range(1,101):
                            result_50=sample_50(file_path)
                            df_50,_,type=result_50
                            graph=Compute(df_50)
                            f=graph.toString()
                            graphs_50.append(str(f))
                            with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                                pickle.dump(graphs_50,fout)
                                print("50 done")

                            # data = df_to_data(df_50)
                            # score = ts.score.SemBicScore(data, False)
                            # #score.setStructurePrior(0)
                            # graph, bics, times = multi_boss(score, discounts=2,threads=1,starts=1)
                            # with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_subsample_{i}.txt", "w") as fout:
                            #     fout.write(str(graph.toString()))
                            #     #fout.write(str(times)) 
                    elif type=='100SS':
                        # Generating 100 samples, running boss, storing graphs
                        graphs_100SS=[]
                        for i in range(1,101):
                            result_100=sample_100SS(file_path)
                            df_100,_,type=result_100
                            graph=Compute(df_100)
                            f=graph.toString()
                            graphs_100SS.append(str(f))
                            with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                                pickle.dump(graphs_100SS,fout)
                                print("100SS done")
                            # data = df_to_data(df_100)
                            # score = ts.score.SemBicScore(data, False)
                            # #score.setStructurePrior(0)
                            # graph, bics, times = multi_boss(score, discounts=2,threads=1,starts=1)
                            # with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_bootstrap(SS)_{i}.txt", "w") as fout:
                            #     fout.write(str(graph.toString()))
                                #fout.write(str(times))
                    elif type=='100ESS':
                        # Generating 100 samples, running boss, storing graphs
                        graphs_100ESS=[]
                        for i in range(1,101):
                            result_100ESS=sample_100ESS(file_path)
                            df_100ESS,ESS,type=result_100ESS
                            graph=Compute(df_100ESS, ESS)
                            f=graph.toString()
                            graphs_100ESS.append(str(f))
                            with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                                pickle.dump(graphs_100ESS,fout)
                                print("100ESS done")
                            # data = df_to_data(df_100ESS)
                            # cov = td.CovarianceMatrixOnTheFly(data)
                            # cov.setSampleSize(int(ESS))
                            # score = ts.score.SemBicScore(cov)
                            # #score.setStructurePrior(0)
                            # graph, bics, times = multi_boss(score, discounts=2,threads=1,starts=1)
                            # with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_bootstrap(ESS)_{i}.txt", "w") as fout:
                            #         fout.write(str(graph.toString()))
                                    #fout.write(str(times))
                    else:
                        # Generating 100 samples, running boss, storing graphs
                        graphs_split=[]
                        for i in range (1,101):
                            result_split=sample_split(file_path)
                            df_split1,df_split2,type=result_split
                            graph1=Compute(df_split1)
                            graph2=Compute(df_split2)
                            f1=graph1.toString()
                            f2=graph2.toString()
                            graphs_split.append(str(f1))
                            graphs_split.append(str(f2))
                            with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                                pickle.dump(graphs_split,fout)
                                print("Split done")
                            # data1 = df_to_data(df_split1)
                            # data2 = df_to_data(df_split2)
                            # score1 = ts.score.SemBicScore(data1, False)
                            # score2 = ts.score.SemBicScore(data2, False)
                            #score1.setStructurePrior(0)
                            #score2.setStructurePrior(0)
                            # graph1, bics1, times1 = multi_boss(score1, discounts=2,threads=1,starts=1)
                            # graph2, bics2, times2 = multi_boss(score2, discounts=2,threads=1,starts=1)
                            # with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_(1)_{i}.txt", "w") as fout1:
                            #     fout1.write(str(graph1.toString()))
                            #     #fout1.write(str(times1))
                            # with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_(2)_{i}.txt", "w") as fout2:
                            #     fout2.write(str(graph2.toString()))
                                #fout2.write(str(times2))
                
#print(f"Processing file: {file_path}\n")
# #result=sample(file_path)
#print(f'Sampled {file_path}\n')
#filename=os.path.basename(file_path)
'''if isinstance(result,tuple):
df,eff_ss,type= result
if isinstance(eff_ss, int):
print('ESS is integer')
break
data = df_to_data(df)
cov = td.CovarianceMatrix(data)
cov.setSampleSize(int(eff_ss))
score = ts.score.SemBicScore(data, True)
score.setStructurePrior(0)
graph, bics, times = multi_boss(score, discounts=2,threads=1,starts=1)
with open(f"{output_dir}/{filename.replace('.csv','')}{type}.txt", "w") as fout:
fout.write(str(graph.toString()))
fout.write(str(times))
else:
if isinstance(eff_ss, pd.DataFrame):
print('ESS is dataframe')
break
data1 = df_to_data(df)
data2 = df_to_data(eff_ss)
score1 = ts.score.SemBicScore(data1, True)
score2 = ts.score.SemBicScore(data2, True)
score1.setStructurePrior(0)
score2.setStructurePrior(0)
graph1, bics1, times1 = multi_boss(score1, discounts=2,threads=1,starts=1)
graph2, bics2, times2 = multi_boss(score2, discounts=2,threads=1,starts=1)
with open(f"{output_dir}/{filename.replace('.csv','')}{type}.txt", "w") as fout:
fout.write(str(graph.toString()))
fout.write(str(times))

else:
print('Normal data')
break
data,_,type=result
df = df_to_data(data)
score = ts.score.SemBicScore(df, True)
score.setStructurePrior(0)
graph, bics, times = multi_boss(df, discounts=2,threads=1,starts=1)
with open(f"{output_dir}/{filename.replace('.csv','')}{type}.txt", "w") as fout:
fout.write(str(graph.toString()))
fout.write(str(times))'''
#print(filename)
#with open(f"{output_dir}/{filename.replace('.csv','')}.txt", "w") as fout:
#    fout.write('Hello')
#    fout.write('str(times)')
#graph, bics, times = multi_boss(data, discounts=2,threads=1,starts=1)
#with open(f"{output_dir}/{filename.replace('.csv','')}.txt", "w") as fout:
#fout.write(str(graph.toString()))
#fout.write(str(times))

if __name__ == "__main__":
    # Check if folder path is provided
    if len(sys.argv) < 2:
        print("Usage: python run_boss.py <folder_path>")
        sys.exit(1)
    
    # Get the folder path from command-line arguments
    folder_path = sys.argv[1]

    # Check if the folder path exists
    if not os.path.exists(folder_path):
        print(f"Error: The folder path '{folder_path}' does not exist.")
        #print(folder_path)
        sys.exit(1)
    main(folder_path)