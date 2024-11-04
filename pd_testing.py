import numpy as np
import pandas as pd

from sample import er_dag, sf_in, sf_out, randomize_graph, corr, cov, simulate, standardize

import jpype
import jpype.imports

jpype.startJVM("-Xmx4g", classpath="tetrad-current.jar")

import java.util as util
import edu.cmu.tetrad.graph as tg
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.algcomparison as ta

import translate


def construct_graph(g, nodes, cpdag=True):
    graph = tg.EdgeListGraph(nodes)
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if g[i, j]: graph.addDirectedEdge(b, a)
    if cpdag: graph = tg.GraphTransforms.cpdagForDag(graph)
    return graph


def run_sim(n, p, ad, sf, c, rep):

    g = er_dag(p, ad=ad)
    if sf[0]: g = sf_out(g)
    if sf[1]: g = sf_in(g)
    g = randomize_graph(g)
    _, B, O = corr(g)

    gaus_err = lambda *x: np.random.normal(0, np.sqrt(x[0]), x[1])
    gumb_err = lambda *x: np.random.gumbel(0, np.sqrt(6.0 / np.pi**2 * x[0]), x[1])
    exp_err = lambda *x: np.random.exponential(np.sqrt(x[0]), x[1])
    lapl_err = lambda *x: np.random.laplace(0, np.sqrt(x[0] / 2), x[1])
    unif_err = lambda *x: np.random.uniform(-np.sqrt(3 * x[0]), np.sqrt(3 * x[0]), x[1])

    X = simulate(B, O, n, gaus_err)
    if standardize_data: X = standardize(X)

    df = pd.DataFrame(X, columns=[f"X{i + 1}" for i in range(p)])
    tmp = pd.DataFrame(X, columns=[f"X{i + 1}" for i in range(p)])
    data = translate.df_to_data(df)
    nodes = data.getVariables()
    cpdag = construct_graph(g, nodes)

    score = ts.score.SemBicScore(data, True)
    score.setPenaltyDiscount(c)
    score.setStructurePrior(0)

    algs = []
    graphs = []

    algs.append("boss")
    boss = ts.Boss(score)
    boss.setUseBes(boss_bes)
    boss.setNumStarts(boss_starts)
    boss.setNumThreads(boss_threads)
    boss.setUseDataOrder(False)
    boss.setResetAfterBM(True)
    boss.setResetAfterRS(False)
    boss.setVerbose(False)
    boss = ts.PermutationSearch(boss)
    graphs.append(boss.search())

    return (tg.GraphUtils.replaceNodes(cpdag, nodes), data,
            [(alg, tg.GraphUtils.replaceNodes(graphs[i], nodes)) for i, alg in enumerate(algs)])


reps = 1

unique_sims = [(n, p, ad, sf, c)
               for ad in [10]
               for p in [379]
               for n in [400]
               for sf in [(1, 0)]
               for c in [12, 8, 4]]

standardize_data = True

stats = [ta.statistic.AdjacencyPrecision(),
         ta.statistic.AdjacencyRecall(),
         ta.statistic.OrientationPrecision(),
         ta.statistic.OrientationRecall(),
         ta.statistic.BicDiff(),
         ta.statistic.NumberOfEdgesEst()]


boss_bes = False
boss_starts = 1
boss_threads = 4


results = []

for n, p, ad, sf, c, rep in [(*sim, rep) for sim in unique_sims for rep in range(reps)]:
    print(f"samples: {n} | variables: {p} | avg_deg: {ad} | scale-free: {sf} | discount: {c} | rep: {rep}")
    true_cpdag, data, algs = run_sim(n, p, ad, sf, c, rep)
    for alg, est_cpdag in algs: results.append([n, p, ad, sf, alg, c, rep] + [stats[i].getValue(true_cpdag, est_cpdag, data) for i in range(len(stats))])

param_cols = ["samples", "variables", "avg_deg", "scale-free", "algorithm", "discount", "run"]
stat_cols = ["adj_pre", "adj_rec", "ori_pre", "ori_rec", "bic_delta", "num_edges"]
df = pd.DataFrame(np.array(results), columns=param_cols+stat_cols)
for col in stat_cols: df[col] = df[col].astype(float)

param_cols.remove("run")
print(f"\n\nreps: {reps}\n")
print(df.groupby(param_cols)[stat_cols].agg("mean").round(2).to_string())
