import sys
import os


path = "/home/miran045/shared/projects/Rawls_ABCD_GANGO_CDA/cifti_csv/"
# completed = os.listdir("graphs/")

batch = int(sys.argv[1])
for fname in os.listdir(path):

    # if f"{fname.replace('.csv','')}.txt" in completed:
    #     continue

    with open(f"sbatch/{fname.replace('.csv','')}.sbatch", "w") as f:
        f.write(f"#!/bin/bash -l\n\n#SBATCH --job-name={fname}\n#SBATCH --time=48:00:00\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=1\n#SBATCH --cpus-per-task=1\n#SBATCH --mem=16g\n#SBATCH --tmp=16g\n#SBATCH -o ./logs/{fname.replace('.csv','')}.out\n#SBATCH -p agsmall\n\npython3 run_boss.py {path} {fname}")

    exe = []
    exe.append("module load python3/3.10.9_anaconda2023.03_libmamba")
    exe.append("module load java/openjdk-17.0.2")
    exe.append(f"sbatch sbatch/{fname.replace('.csv','')}.sbatch")
    os.system(";".join(exe))

    batch = batch - 1
    if batch == 0: break
