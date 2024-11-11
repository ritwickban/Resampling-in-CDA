import pandas as pd
import jpype
import jpype.imports
import os

try:
    jpype.startJVM("-Xmx16g", classpath="../tetrad-current.jar")
    print("JVM Started")
except OSError:
    print("JVM already started")

import java.util as util
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.search as ts

from dao import er_dag, randomize_graph,sf_in,sf_out,corr,simulate,standardize
from translate import mat_to_graph

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


variables = [10, 50, 250]
avg_deg = [2, 4, 12]
sample_sizes = [40, 80, 160, 320, 640, 1280, 2560, 5120]
st_type = ['ER', 'SF']

# Assuming `simulate`, `corr`, `mat_to_graph`, `df_to_data`, and `standardize` functions are defined elsewhere.
for st in st_type:
    for p in variables:
        for ad in avg_deg:
            if p > ad:
                if st == 'ER':
                    # Generate ER graph
                    g = er_dag(p, ad=ad)
                elif st == 'SF':
                    # Generate SF graph with both in and out scaling
                    g = er_dag(p, ad=ad)
                    g = sf_in(g)
                    g = sf_out(g)

                # Calculate correlation matrix and simulate base matrix with 10240 rows
                _, B, O = corr(g)
                X1=simulate(B,O,5)
                df=pd.DataFrame(X1,columns=[f"X{i+1}" for i in range(p)])
        
                data= df_to_data(df)
                nodes= data.getVariables()

                # Save the base graph and data
                base_dir = f"Data/{st}/Variable_{p}/AD_{ad}/"
                
                
                graph = mat_to_graph(g, nodes)  # Convert to graph format with column names
                with open(f"{base_dir}/graph.txt", 'w') as file:
                    file.write(str(graph))

                # Sampling loop
                for i in range(200):
                    X_base = simulate(B, O, 10240)  # Base matrix with 10240 rows
                    df_base = pd.DataFrame(X_base, columns=[f"X{i+1}" for i in range(p)])
                    export_base=f"Data/{st}/Variable_{p}/AD_{ad}/n_10240/"
                    df_base.to_csv(f"{export_base}_Sample{i+1}.csv",index=False)
                    print(f"Base done for iteration{i}\n")

                    for size in sample_sizes:
                        # Sample rows (not columns) without replacement
                        sampled_df = df_base.sample(n=size, replace=False)
                        
                        # Standardize the sampled data
                        sampled_df = standardize(sampled_df.to_numpy())
                        sampled_df = pd.DataFrame(sampled_df, columns=[f"X{i+1}" for i in range(p)])

                        # Save standardized sampled data
                        sample_dir = f"{base_dir}/n_{size}/"
                        sampled_df.to_csv(f"{sample_dir}_sample{i+1}.csv", index=False)
                    print(f"Sampling done for {size}\n")
                print(f"Finished for {st} Var={p} /AD={ad}")
            else:
                print("YOU'RE DUMB! YOU CAN'T CODE! ")
            



#g = er_dag(p,ad=ad)
#print(f"ER DAG {g}\n")
#g=sf_in(g)
#f= randomize_graph(g)
#R,B,O = corr(g)
#X=simulate(B,O,100)
#X=standardize(X)
#df=pd.DataFrame(X,columns=[f"X{i+1}" for i in range(p)])