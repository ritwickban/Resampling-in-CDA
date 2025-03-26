import sys
import os
import pandas as pd
import jpype
import numpy as np
import jpype.imports
import pickle
import shutil
from boss import boss
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

def read(filepath):
    """Sample 90% of the data."""
    try:
            df = pd.read_csv(filepath)
            # samdf = df.sample(frac=0.9)
            
            return df, None, 'fun'
    except Exception as e:
            print(f"Error processing {filepath} for type '90': {e}")
            return None


def run_fges(score, discount=1, starts=1, threads=1):
    
    score.setStructurePrior(0)


    score.setPenaltyDiscount(discount)
    score.setUsePseudoInverse(True)
        
    fges = ts.Fges(score)
    fges.setFaithfulnessAssumed(False)
    fges.setNumThreads(threads)
    fges.setVerbose(False)
    graph = fges.search()

    
    return graph

def construct_graph(g, nodes, cpdag=True):
    graph = tg.EdgeListGraph(nodes)

    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if g[i, j]: graph.addDirectedEdge(b, a)

    if cpdag: graph = tg.GraphTransforms.dagToCpdag(graph)

    return graph
# Transforms dataframe to Tetrad dataframe, computes covariance matrix and then scomputes SEMBIC score and runs boss.
def Compute(df, discount=1, ESS=None): 
    data = df_to_data(df) 
    rcm = tsc.RealCovarianceMatrix(data.getDoubleData().toArray())
    cov = td.CovarianceMatrix(data.getVariables(), rcm.compute(True), data.getNumRows())
    score = ts.score.SemBicScore(cov)
    graph = run_fges(score, discount=discount, threads=1, starts=1)
    return graph

def main(folderpath):
    if folderpath.endswith(".csv"):
        base=os.path.dirname(folderpath)
        outputdir=os.path.join(base,"No_resam_FGES")
        shutil.rmtree(outputdir, ignore_errors=True)
        os.makedirs(outputdir,exist_ok=True)
        types=['None_PD1','None_PD2']
        for type in types:
            typedir=os.path.join(outputdir,type)
            os.makedirs(typedir,exist_ok=True)
            if type=='None_PD1':
                # Generating 100 samples, running boss, storing graphs
                graphs_90=[]
                result_90=read(folderpath)
                df_90,_,_=result_90
                graph=Compute(df_90,discount=1)
                f=graph.toString()
                graphs_90.append(str(f))
                with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                    pickle.dump(graphs_90,fout) 
                    print("PD1 done")
                # with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_subsample_{i}.txt", "w") as fout:
                #     fout.write(str(graph.toString()))
            elif type=='None_PD2':
                # Generating 100 samples, running boss, storing graphs
                graphs=[]
                result_90=read(folderpath)
                df_90,_,_=result_90
                graph=Compute(df_90,discount=2)
                f=graph.toString()
                graphs.append(str(f))
                with open(f"{typedir}/{os.path.basename(folderpath).replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                    pickle.dump(graphs,fout)
                    print("PD2 done")
            
            
                

    else:
        output_dir = os.path.join(folderpath, "No_resam_FGES")
        #print(output_dir)
        shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir, exist_ok=True)
        for filename in os.listdir(folderpath):
            if filename.endswith(".csv"):
                file_path = os.path.join(folderpath, filename)
                types=['None_PD1','None_PD2']
                for type in types:
                    type_dir=os.path.join(output_dir,type)
                    os.makedirs(type_dir,exist_ok=True)
                    if type=='None_PD1':
                        graphs_90=[]
                        # Generating 100 samples, running boss, storing graphs
                        result_90=read(file_path)
                        df_90,_,_=result_90
                        graph=Compute(df_90,discount=1)
                        f=graph.toString()
                        graphs_90.append(str(f))
                        with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                            pickle.dump(graphs_90,fout)
                            print("PD1 done")
                    elif type=='None_PD2':
                        graphs=[]
                        # Generating 100 samples, running boss, storing graphs
                        result_90=read(file_path)
                        df_90,_,_=result_90
                        graph=Compute(df_90,discount=2)
                        f=graph.toString()
                        graphs.append(str(f))
                        with open(f"{type_dir}/{filename.replace('.csv','')}_{type}_all_graphs.pkl", "wb") as fout:
                            pickle.dump(graphs,fout)
                            print("PD2 done")
                            

                            
                
    jpype.shutdownJVM()

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