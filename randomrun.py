import os

#files = ['sbatch/ER_Variable_100_AD_2_n_10240.sh','sbatch/ER_Variable_100_AD_6_n_10240.sh']
for files in os.listdir('sbatch_FGES/'):
        #print(files)
        if files.startswith("SF_Variable_100_AD_2_n_10240"):
                #print(files)
                exe = []
                exe.append("module load python3/3.10.9_anaconda2023.03_libmamba")
                exe.append("module load java/openjdk-17.0.2")
                exe.append(f"sbatch sbatch_FGES/{files}")
                os.system(";".join(exe))