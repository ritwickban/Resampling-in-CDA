import sys
import os

import numpy as np
import pandas as pd

import jpype
import jpype.imports


BASE_DIR = "/home/erichk/andr1017"
sys.path.append(BASE_DIR)
jpype.startJVM("-Xmx15g", classpath=[f"{BASE_DIR}/tetrad-gui-7.6.3-launch.jar"])

import java.util as util
import edu.cmu.tetrad.data as td
import edu.cmu.tetrad.search as ts


def df_to_data(df):
    cols = df.columns
    values = df.values
    n, d = df.shape

    variables = util.ArrayList()
    for col in cols:
        variables.add(td.ContinuousVariable(str(col)))

    databox = td.DoubleDataBox(n, d)

    for col, var in enumerate(values.T):
        for row, val in enumerate(var):
            databox.set(row, col, val)

    return td.BoxDataSet(databox, variables)


def multi_boss(df, discounts=[2], starts=1, threads=1):

    data = df_to_data(df)
    score = ts.score.SemBicScore(data, True)
    score.setStructurePrior(0)

    order = None
    bics = []
    times = []

    for discount in discounts:

        score.setPenaltyDiscount(discount)
        boss = ts.Boss(score)
        boss.setUseBes(False)

        boss.setResetAfterBM(True)
        boss.setResetAfterRS(False)

        boss.setUseDataOrder(order != None)
        boss.setNumStarts(starts)
        if starts > 1: starts = 1

        boss.setNumThreads(threads)
        boss.setVerbose(False)

        search = ts.PermutationSearch(boss)
        if order != None: search.setOrder(order)

        graph = search.search()
        order = search.getOrder()
        bics += [bic for bic in boss.getBics()]
        times += [time for time in boss.getTimes()]

    return graph, bics, times


path, fname = sys.argv[1:3]
df = pd.read_csv(path + fname)
graph, bics, times = multi_boss(df, discounts=[16, 2], starts=10)

with open(f"graphs/{fname.replace('.csv','')}.txt", "w") as fout:
    fout.write(str(graph.toString()))
