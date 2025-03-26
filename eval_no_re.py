from visualize import graphs_to_probs
import os
import pickle

def process_directory(path, reps,temp,resample):
    #print(path)
    #quit()
    files = os.listdir(path)
    #print(files)
    #quit()
    for file in files:
        #print(file)
        if file.endswith(".pkl"):
            file_path = os.path.join(path, file)
            #print(f"Processing file: {file}")
            with open(file_path, "rb") as f:
                pickled_graphs = pickle.load(f)
            probs=graphs_to_probs(pickled_graphs)

            print(probs)
            quit()
            #print(file.split('_90',)[0])
        sample = file.split('Sample_')[1].split('_')[0]
        # print(sample)
        # print('\n')
        # print(probs)
        # print('\n')
        # output_file = os.path.join(temp)
        # os.makedirs(output_file,exist_ok=True)
        # with open(f'{output_file}/BOSS_analyzed_{sample}.pkl', "wb") as f:
        #     pickle.dump(probs, f)





# Load the graphs
variables = [20,100]
avg_deg = [2,6]
sample_sizes = [40, 80, 160, 320, 640, 1280, 2560, 5120, 10240]
#sample_sizes = [40]
reps=1
st_type = ['ER', 'SF']
resamples=['None_PD1','None_PD2']
for st in st_type:
    for p in variables:
        for ad in avg_deg:
            for sample in sample_sizes:
                #if (p==20) and (int(sample)==40): continue
                print(st,ad,p,sample)
                print('\n')
                for resample in resamples:
                    if (p==100) and (int(sample)<320): continue
                    base_path = f"Data/{st}/Variable_{p}/AD_{ad}/n_{sample}/No_resam_Boss/{resample}/"  # Base directory containing all subdirectories.
                    temp=base_path.replace('Data','No_resam_BOSS')
                    process_directory(base_path,reps,temp,resample)