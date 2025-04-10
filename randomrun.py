import os
import sys
for files in os.listdir('sbatch_PC/'):

        if files.endswith('.sbatch'):
                # print(files)
                exe = []
                exe.append("module load python3/3.10.9_anaconda2023.03_libmamba")
                exe.append("module load java/openjdk-17.0.2")
                exe.append(f"sbatch sbatch_PC/{files}")
                os.system(";".join(exe))


#find Data -name "Learnt_graph_BOSS" -type d -exec rm -r {} +
# (files.startswith("BOSS_ER_20_2_40") | files.startswith('BOSS_SF_20_2_40'))