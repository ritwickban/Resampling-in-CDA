import os
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss
from sklearn.calibration import calibration_curve
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.preprocessing import Binarizer
import matplotlib.pyplot as plt

base = '/home/erichk/shared/Resampling-in-CDA/'

gss = ['ER', 'SF']
ps = [20, 100]
ads = [2, 6]
ns = [40, 80, 160, 320, 640, 1280, 2560, 5120, 10240]
sts = ['None_PD1','None_PD2'] # Split

# Create a list to store the results
results = []

for gs in gss:
    for st in sts:
        for p in ps:
            for ad in ads:
                for n in ns:

                    y_true = []
                    y_prob = []
                    brier = []
                    f1=[]
                    calib=[]
                    if (p == 100) and (int(n) < 320): 
                        continue
                    # if (p == 20) and (int(n) == 40):
                    #     continue
                    if p==20:
                        num_graphs=250
                    else:
                        num_graphs=50
                    for i in range(num_graphs):
                        path = base + f'Data/{gs}/Variable_{p}/AD_{ad}/'
                        with open(path + f'graph{i+1}.txt') as f: 
                            edges = [edge.split()[1:] for edge in f.read().split('\n\n')[1].replace('Graph Edges:\n','Graph Edges:').split("Graph Edges:")[1].split("\n") if edge != ""]
                        keys = [tuple(sorted([edge[0], edge[2]], reverse=True)) for edge in edges]
                        path = base + f'No_resam_FGES/{gs}/Variable_{p}/AD_{ad}/n_{n}/No_resam_FGES/{st}/' # Change this path to the location of the processed output, Modified for FGES right now!
                        with open(path + f'FGES_analyzed_{i+1}.pkl', 'rb') as f: # Change this to the name of the processed output file, Modified for FGES right now!
                            probs = pickle.load(f)
                            #print(f"FGES_analyzed_{i+1}.pkl\n")
                        
                        for j in range(p):
                            for k in range(j):
                                key = tuple(sorted([f'X{j+1}', f'X{k+1}'], reverse=True))
                                y_true.append(int(key in keys))
                                y_prob.append(0)
                                if key in probs: 
                                    y_prob[-1] += round(sum(probs[key].values()), 2)

                        #brier.append(brier_score_loss(y_true, y_prob))
                    # print(len(y_true),len(y_prob))
                    
                    #print("y_prob:",y_prob, '\n', 'type:', st)
                    # if y_prob>1:
                    #     print(y_prob) 
                    #     quit()
                    brier=brier_score_loss(y_true, y_prob)
                    # f1=f1_score(y_true, y_prob, average='weighted')
                    # recall =f1_score(y_true, y_prob, average='macro')
                    # precision =f1_score(y_true, y_prob, average='micro')
                    # print("y_true:",y_true)
                    # print("y_prob:",y_prob)
                    #quit()
                    threshold = 0.5  # You can adjust this threshold as needed
                    y_pred = Binarizer(threshold=threshold).transform(np.array(y_prob).reshape(-1, 1))
                    f1=f1_score(y_true, y_pred)
                    precision =precision_score(y_true, y_pred)
                    recall =recall_score(y_true, y_pred)
                    # prob_true,prob_pred=calibration_curve(y_true,y_prob,n_bins=5)
                    # print(prob_true,prob_pred)
                    
                    # prob_tr=np.histogram(y_prob, bins=5, range=[0,1])[0] / len(y_prob)
                    # prob_pr=np.histogram(y_true, bins=5, range=[0,1])[0] / len(y_true)
                    # print("prob_tr:",prob_tr,"prob_pr:",prob_pr)
                    n_bins=10
                    bins= np.histogram(y_true, bins=n_bins, range=[0,1])[1]
                    
                    #prob_pr=np.histogram(y_true, bins=5, range=[0,1])[0] / len(y_true)
                    masks = [(bins[i] <= y_prob) & (y_prob <= bins[i + 1]) for i in range(n_bins - 1)]

                    # Compute oi, pi, and ei, handling empty masks
                    pi = np.array([np.sum(np.array(np.ones_like(y_true))[mask]) / len(y_true) for mask in masks])
                    oi = np.array([np.sum(np.array(y_true)[mask]) / len(y_true) for mask in masks])
                    ei = np.array([np.sum(np.array(y_prob)[mask]) / len(y_prob) for mask in masks])

                    # Calculate Expected Calibration Error (ECE)
                    ece = np.sum(pi * np.abs(oi - ei))

                    

                    # Compute the calibration curve
                    # prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10)

                    # # Plot the calibration curve
                    # plt.figure()
                    # plt.plot(prob_pred, prob_true, marker='o', linestyle='-', label='Model')
                    # plt.plot([0,1], [0,1], linestyle='--', color='gray', label='Perfectly calibrated')
                    # plt.xlabel("Predicted Probability")
                    # plt.ylabel("True Probability")
                    # plt.title("Calibration Curve")
                    # plt.savefig(f'Calibration/calibration_curve_{gs}_{st}_{p}_{ad}_{n}.png')
                    # plt.legend()
                    # plt.show()
            

    
                    #Calculate mean and std deviation of Brier scores
                    # mean_brier = np.mean(brier)
                    # std_brier = np.std(brier)
                    # mean_ece=np.mean(ece)
                    # std_ece=np.std(ece)

                    #Append the results to the list
                    results.append({
                        'Graph Type': gs,
                        'Penalty Discount': st,
                        'Variable Type': p,
                        'Average Degree': ad,
                        'Sample Size': n,
                        'Brier': brier,
                        'F1': f1,
                        'Recall': recall,
                        'Precision': precision,
                        "ECE": ece
                    })

                    # Print scores
                    print(gs, st, p, ad, n, "Brier:",brier, "ece:", ece, "F1:", f1, "Recall:", recall, "Precision:", precision)

# Convert the results list into a pandas DataFrame
df = pd.DataFrame(results)

# Save the DataFrame to a CSV file
output_csv_path = 'brier_scores_FGES_nores.csv' # Change this to the desired output path, Modified for FGES right now!
df.to_csv(output_csv_path, index=False)

print(f"Results have been saved to {output_csv_path}")
