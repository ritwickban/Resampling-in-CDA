import pandas as pd
import jpype
import jpype.imports
import os

try:
    jpype.startJVM("-Xmx16g", classpath="tetrad-current.jar")
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


variables = [20, 100]
avg_deg = [2, 6]
sample_sizes = [40, 80, 160, 320, 640, 1280, 2560, 5120, 10240]
st_type = ['ER', 'SF']

for st in st_type:
    for p in variables:
        for ad in avg_deg:
            if p > ad:
                if p == 20:
                    num_graphs = 250
                else:
                    num_graphs = 50
                    
                for i in range(num_graphs):
                    if st == 'ER':
                        # Generate ER graph
                        g = er_dag(p, ad=ad)
                    elif st == 'SF':
                        # Generate SF graph with both in and out scaling
                        g = er_dag(p, ad=ad)
                        for _ in range(100):
                            g = sf_in(g)
                            g = sf_out(g) # Bryan - Keep one of the scale free functions. Ask Erich for clarification

                    # Calculate correlation matrix and simulate base matrix with 10240 rows
                    _, B, O = corr(g)
                    X1 = simulate(B, O, 5)
                    df = pd.DataFrame(X1, columns=[f"X{i+1}" for i in range(p)])

                    data = df_to_data(df)
                    nodes = data.getVariables()

                    # Define the base directory path and create it
                    base_dir = f"Data/{st}/Variable_{p}/AD_{ad}"
                    os.makedirs(base_dir, exist_ok=True)

                    # Convert to graph format with column names and save
                    graph = mat_to_graph(g, nodes, False)
                    with open(f"{base_dir}/graph{i+1}.txt", 'w') as file:
                        file.write(str(graph))

                    # Export the base data matrix with 10240 rows
                    for sample in sample_sizes:
                        X_base = simulate(B, O, sample)
                        df_base = pd.DataFrame(X_base, columns=[f"X{i+1}" for i in range(p)])
                        export_base_dir = f"{base_dir}/n_{sample}"
                        os.makedirs(export_base_dir, exist_ok=True)
                        df_base.to_csv(f"{export_base_dir}/Sample_{i+1}.csv", index=False)
                        print(f"Base matrix done for iteration {i+1}\n")


                print(f"Finished for {st} with Variables={p}, AD={ad}\n")
                



#g = er_dag(p,ad=ad)
#print(f"ER DAG {g}\n")
#g=sf_in(g)
#f= randomize_graph(g)
#R,B,O = corr(g)
#X=simulate(B,O,100)
#X=standardize(X)
#df=pd.DataFrame(X,columns=[f"X{i+1}" for i in range(p)])
