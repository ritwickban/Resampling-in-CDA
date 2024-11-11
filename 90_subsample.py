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

source_dir="Data/"
target_dir = "Data/Sampled/90_subsample/"
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
			
			#print(basedir)
			
			for i in range(1,201):
				targpath=os.path.join(target_dir,f"{basedir}")
				os.makedirs(targpath,exist_ok=True)
				#samdf=df.sample(frac=0.9,random_state=100)
				resampath=os.path.join(targpath,f"Resampled_{i}.csv")
				#samdf.to_csv(resampath,index=False)
				print(f"Saved {resampath}")
		
		

#df=pd.read_csv('')


