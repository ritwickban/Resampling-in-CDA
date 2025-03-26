import pickle
import os
base = '/home/erichk/shared/Resampling-in-CDA/'

gss = ['ER', 'SF']
ps = [20, 100]
ads = [2, 6]
ns = [40, 80, 160, 320, 640, 1280, 2560, 5120, 10240]
sts = ['100ESS', '100SS', '50', '90']


for gs in gss:
    for st in sts:
        for p in ps:
            for ad in ads:
                for n in ns:
                     ad = 6
                     n=320
                     st = '100ESS'
                     if (p == 100) and (int(n) < 320): 
                        continue
                    
                     path = base + f'Data/{gs}/Variable_{p}/AD_{ad}/n_{n}/Learnt_graphs_fges/{st}/'            
                     with open(path + f'Sample_{1}_{st}_all_graphs.pkl', 'rb') as f: # Change this to the name of the processed output file, Modified for FGES right now!
                            graphs = pickle.load(f)
                            for graph in graphs:
                                edges = [
                                    edge.split()[1:]
                                    for edge in graph.split('\n\n')[1].split("Graph Edges:\n")[1].split("\n")
                                    if edge.strip()
                                ]
                                print(edges)
                                print("\n")
                     quit()

                     #print(graphs)
                     #quit()
                    #  with open (path + f'FGES_analyzed_{6}.p', 'rb') as f1: # Change this to the name of the processed output file, Modified for FGES right now!
                    #         probs1 = pickle.load(f1)
                     
                    #  print(probs)
                    #  print('\n\n\n\n\n')
                    #  print(probs1)
                    #  if probs==probs1:
                    #      print("Same")
                    #  else:
                    #         print("Different")
                    #  quit()