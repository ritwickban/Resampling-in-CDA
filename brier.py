import os
import pickle
import numpy as np

from sklearn.metrics import brier_score_loss

base = '/home/erichk/shared/Resampling-in-CDA/'

gss = ['ER', 'SF']
ps =  [20, 100]
#ps =  [20]
ads = [2, 6]
#ads = [6]
ns =  [40, 80, 160, 320, 640, 1280, 2560, 5120, 10240]
sts = ['100ESS', '100SS', '50', '90']
# sts = ['50', '90']

for gs in gss:
    for st in sts:

        print()

        for p in ps:
            for ad in ads:
                for n in ns:

                    y_true = []
                    y_prob = []
                    brier=[]
                    if (p==100) and (int(n)<320): continue
                    for i in range(1, 51):
                        path = base + f'Data/{gs}/Variable_{p}/AD_{ad}/'
                        with open(path + f'graph{i}.txt') as f: edges = [edge.split()[1:] for edge in f.read().split("Graph Edges:\n")[1].split("\n") if edge != ""]
                        keys = [tuple(sorted([edge[0], edge[2]], reverse=True)) for edge in edges]
                        path = base + f'Analysed/{gs}/Variable_{p}/AD_{ad}/n_{n}/processed_output/{st}/Analysed/'
                        with open(path + f'Boss_analyzed_{i}.p', 'rb') as f: 
                            probs = pickle.load(f)
                            # print(probs)
                            # quit()

                        for j in range(p):
                            for k in range(j):
                                key = tuple(sorted([f'X{j}', f'X{k}'], reverse=True))
                                
                                y_true.append(int(key in keys))
                                y_prob.append(0)
                                if key in probs: 
                                    #print("Key is in probs")
                                    y_prob[-1] += round(sum(probs[key].values()), 2)

                        brier.append(brier_score_loss(y_true, y_prob))
                    print(st, gs, p, ad, n, np.mean(brier), np.std(brier))
