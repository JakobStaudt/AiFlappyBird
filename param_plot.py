import train
import itertools
import json
import matplotlib.pyplot as plt

MAX_GENERATIONS = 10

MUTATION_RATES = [0.05, 0.1, 0.2, 0.5]
CHILD_METHODS = ["cloning", "crossover_pick", "crossover_avg"]

RUNS_PER_PARAMSET = 10


param_scores = {}
for params in list(itertools.product(MUTATION_RATES, CHILD_METHODS)):
    mutation_rate, child_method = params

    avg_scores = [0 for _ in range(MAX_GENERATIONS)]
    all_scores = []
    for _ in range(RUNS_PER_PARAMSET):
        gen_scores = train.do_training(child_method=child_method, mutation_rate=mutation_rate, max_generations=MAX_GENERATIONS)
        for i, score in enumerate(gen_scores):
            avg_scores[i] += score
        all_scores.append(gen_scores)
    avg_scores = [s / MAX_GENERATIONS for s in avg_scores]

    param_scores[(mutation_rate, child_method)] = (avg_scores, all_scores)

with open("training_data.json", encoding="utf-8") as f:
    json.dump(param_scores, f)

for params, (avg_scores, all_scores) in param_scores:
    plt.plot(avg_scores, label=str(params))
plt.legend()
plt.show()