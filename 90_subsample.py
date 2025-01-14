import pandas as pd
import jpype
import jpype.imports
import os

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


source_dir="Data/"
target_dir = "Data/Sampled/90_subsample/"
algos = ['PC','FGES','BOSS','DAGMA']
for algo in algos:
	for root, dirs, files in os.walk(source_dir):
		for file in files:
			if file.endswith('.csv'):
				filepath=os.path.join(root,file)
				df=pd.read_csv(filepath)
				#print(df.head())
				#print(filepath)
				#print(os.getcwd())
				#print(len(samdf))
				#print(samdf.head())
				#sampath=f"{filepath}/{file}/"
				relpath=os.path.relpath(filepath,source_dir)
				basedir,_ = os.path.splitext(relpath)
				
				print(basedir)
				#for i in range(1,201):
					#targpath=os.path.join(target_dir,f"{basedir}")
					#os.makedirs(targpath,exist_ok=True)
					#samdf=df.sample(frac=0.9,random_state=100)

					#if (algo=='BOSS'):
						#graph, bics, times = multi_boss(df, discounts=[2], starts=10)
						#with open(f"graphs/{fname.replace('.csv','')}.txt", "w") as fout:
							#fout.write(str(graph.toString()))
					
						


					#resampath=os.path.join(targpath,f"Resampled_{i}.csv")
					#samdf.to_csv(resampath,index=False)
					#print(f"Saved {resampath}")



