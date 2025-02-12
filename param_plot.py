import train
import itertools
import json
import matplotlib.pyplot as plt
import time
from multiprocessing import Queue
from multiprocessing import Pool

MAX_GENERATIONS = 100

MUTATION_RATES = [0.01, 0.1, 0.2, 0.5, 1]
CHILD_METHODS = ["cloning", "crossover_pick", "crossover_avg"]

RUNS_PER_PARAMSET = 100

def run_thread(params,):
    mutation_rate, child_method = params

    avg_scores = [0 for _ in range(MAX_GENERATIONS)]
    all_scores = []
    for _ in range(RUNS_PER_PARAMSET):
        gen_scores = train.do_training(child_method=child_method, mutation_rate=mutation_rate, max_generations=MAX_GENERATIONS)
        for i, score in enumerate(gen_scores):
            avg_scores[i] += score
        all_scores.append(gen_scores)
    print("Calculating avg scores")
    avg_scores = [s / RUNS_PER_PARAMSET for s in avg_scores]
    print("Pushing into queue")
    return (params, avg_scores, all_scores)

if __name__ == "__main__":
    result_queue = Queue()

    print("Total runs for this training:")
    total_runs = MAX_GENERATIONS * len(MUTATION_RATES) * len(CHILD_METHODS) * RUNS_PER_PARAMSET
    print(total_runs)
    print("Expected time")
    print(f"{total_runs * 2 / 60} minutes")

    param_options = list(itertools.product(MUTATION_RATES, CHILD_METHODS))

    p = Pool()
    retvals = p.map(run_thread, param_options)

    print("All processes completed")

    param_scores = {}

    for (params, avg_scores, all_scores) in retvals:
        param_scores[str(params)] = (avg_scores, all_scores)
    
    print("Writing data to file")

    with open(f"training_data_{int(time.time())}.json", "w", encoding="utf-8") as f:
        json.dump(param_scores, f, indent=4)

    print("Plotting")

    for params, (avg_scores, all_scores) in param_scores.items():
        plt.plot(avg_scores, label=params)
    plt.legend()
    plt.show()
