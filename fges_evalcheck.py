file_path='Data/ER/Variable_20/AD_2/n_80/processed_output/90/Sample_1_90_subsample_1.txt'
with open(file_path, 'r') as f:
       print(f.read().split('\n\n')[1].split("Graph Edges:\n")[1].split("\n"))
        # edges = [
        #     edge.split()[1:]
        #     for edge in 
        #     if edge.strip()
        # ]
        # print(edges)