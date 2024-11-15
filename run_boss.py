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

def sample(filepath):
    types=['90','50','100SS','100ESS','Split']
    for type in types:
        if type=='90':
            for i in range (1,100):
                try:
                    df=pd.read_csv(filepath)
                    samdf=df.sample(frac=0.9,random_state=100)
                    return samdf
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
                    return None
        elif type=='50':
            for i in range (1,100):
                try:
                    df=pd.read_csv(filepath)
                    samdf=df.sample(frac=0.5,random_state=100)
                    return samdf
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
                    return None
        elif type=='100SS':
            for i in range (1,100):
                try:
                    df=pd.read_csv(filepath)
                    samdf=df.sample(frac=1,replace=True,random_state=100)
                    return samdf
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
                    return None
        elif type=='100ESS':
            for i in range(1,100):
                try:
                    df=pd.read_csv(filepath)
                    rng=np.random.default_rng()
                    idxs=rng.choice(len(df),size=len(df),replace=True)
                    _,counts=np.unique(idxs, return_counts=True)
                    eff_ss = np.sum(counts)**2 / np.sum(np.power(counts, 2))
                    samdf = pd.DataFrame(df[idxs, :], columns=df.columns)
                    #samdf=df.sample(frac=1,random_state=100)
                    return samdf
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
                    return None
        else:
            try:
                df=pd.read_csv(filepath)
                samdf=df.sample(frac=0.9,random_state=100)
                return samdf
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
                return None

def multi_boss(df, discounts=[2], starts=1, threads=1):

    data = df_to_data(df)
    score = ts.score.SemBicScore(data, True)
    score.setStructurePrior(0)

    order = None
    bics = []
    times = []

    for discount in discounts:

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

def main(folderpath):

    output_dir = os.path.join(folderpath, "processed_output")
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(folderpath):
        if filename.endswith(".csv"):
            file_path = os.path.join(folderpath, filename)
            
            print(f"Processing file: {file_path}\n")
            data=sample(file_path)
            filename=os.path.basename(file_path)
            #print(filename)
            #with open(f"{output_dir}/{filename.replace('.csv','')}.txt", "w") as fout:
            #    fout.write('Hello')
            #    fout.write('str(times)')
            graph, bics, times = multi_boss(data, discounts=2,threads=1,starts=1)
            with open(f"{output_dir}/{filename.replace('.csv','')}.txt", "w") as fout:
                fout.write(str(graph.toString()))
                fout.write(str(times))

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