import sys
import os

# Define the base path for the directory structure
base_path = "Data/"
batch = int(sys.argv[1])
os.makedirs("sbatch", exist_ok=True)
# Iterate over each directory structure
sample_sizes=['40', '80', '160', '320', '640', '1280', '2560', '5120', '10240']
for main_dir in ["ER", "SF"]:
    for sub_dir in ["Variable_20", "Variable_100"]:
        for sub_dir1 in ["AD_2", "AD_6"]:
            for sample in sample_sizes:  # Generates n_40, n_80, ..., n_10240
                folder= f"n_{sample}"
                folder_path = os.path.join(base_path, main_dir, sub_dir, sub_dir1, folder)
                #print(folder_path)
                # Check if folder path exists
                #if not os.path.isdir(folder_path):
                    #print(f"{folder_path} hey")
                    #continue
                
                # Define job name and path for SLURM script
                job_name = f"{main_dir}_{sub_dir}_{sub_dir1}_{folder}"
                slurm_script = f"sbatch/{job_name}.sbatch"
                
                # Write the SLURM script for this folder
                with open(slurm_script, "w") as f:
                    f.write(f"#!/bin/bash -l \n #SBATCH --job-name={job_name}\n#SBATCH --time=96:00:00\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=1\n#SBATCH --cpus-per-task=1\n#SBATCH --mem=16g\n#SBATCH --tmp=16g\n#SBATCH -o logs/{job_name}.txt\n#SBATCH -p agsmall\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=baner212@umn.edu\npython3 run_boss.py {folder_path}")
                #print(f"{job_name} and {batch}")

for files in os.listdir('sbatch/'):
    #print(files)
    
    exe = []
    exe.append("module load python3/3.10.9_anaconda2023.03_libmamba")
    exe.append("module load java/openjdk-17.0.2")
    exe.append(f"sbatch sbatch/{files}")
    os.system(";".join(exe))

    batch = batch - 1
    if batch == 0: break