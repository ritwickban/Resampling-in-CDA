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

variables=[10,50,250]
avg_deg=[1,2,6]
sample=[40,80,160,320,640,1280,2560,5120,10240]
st_type=['ER','SF_in', 'SF_out']
for st in st_type:
    for p in variables:             
        for ad in avg_deg:
            if(st=='ER'):
                g=er_dag(p,ad=ad)
                _,B,O=corr(g)
                for n in sample:
                    for i in range(200):
                        X=simulate(B,O,n)
                        df=pd.DataFrame(X,columns=[f"X{i+1}" for i in range(p)])
                        #print(os.getcwd())
                        df.to_csv(f"Data/{st}/Variable_{p}/AD_{ad}/n_{n}/Sample_{i+1}.csv",index=False)
            elif(st=='SF_in'):
                g=er_dag(p,ad=ad)
                g=sf_in(g)
                _,B,O=corr(g)
                for n in sample:
                    for i in range(200):
                        X=simulate(B,O,n)
                        df=pd.DataFrame(X,columns=[f"X{i+1}" for i in range(p)])
                        df.to_csv(f"Data/{st}/Variable_{p}/AD_{ad}/n_{n}/Sample_{i+1}.csv",index=False)
            elif(st=='SF_out'):
                g=er_dag(p,ad=ad)
                g=sf_out(g)
                _,B,O=corr(g)
                for n in sample:
                    for i in range(200):
                        X=simulate(B,O,n)
                        df=pd.DataFrame(X,columns=[f"X{i+1}" for i in range(p)])
                        df.to_csv(f"Data/{st}/Variable_{p}/AD_{ad}/n_{n}/Sample_{i+1}.csv",index=False)
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