import sys
import os
path = "Data/SF/Variable_100/AD_6/n_10240/"
batch = int(sys.argv[1])
os.makedirs("sbatch", exist_ok=True)
for file in os.listdir(path):
    #print(file)
    job_name = f"SF_100_6_10240_{file}"
    slurm_script = f"sbatch/{job_name}.sbatch"
    with open(slurm_script, "w") as f:
        f.write(f"#!/bin/bash -l \n #SBATCH --job-name={job_name}\n#SBATCH --time=96:00:00\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=1\n#SBATCH --cpus-per-task=1\n#SBATCH --mem=16g\n#SBATCH --tmp=16g\n#SBATCH -o logs/{job_name}.txt\n#SBATCH -p agsmall\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=baner212@umn.edu\npython3 run_boss.py {path}{file}")


for files in os.listdir('sbatch/'):
    if "Sample" in files:  
        #print(files)
     exe = []
     exe.append("module load python3/3.10.9_anaconda2023.03_libmamba")
     exe.append("module load java/openjdk-17.0.2")
     exe.append(f"sbatch sbatch/{files}")
     os.system(";".join(exe))

    batch = batch - 1
    if batch == 0: break
