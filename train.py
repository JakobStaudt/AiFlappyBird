import flappy
import random
import torch
from torch import nn
import gui
import time
import pygame

# How many of the best models to keep for the next generation
KEEP_BEST = 5
# How many copies of each of the kept models
CHILD_PER_BEST = 20

MAX_GENERATIONS = 50

# How children are created from best models
# One of cloning, crossover_pick, crossover_avg
CHILD_METHOD = "crossover_pick"

# Stdev of random numbers applied to weights during mutation
MUTATION_RATE = 0.3
# Exponent used to scale mutation rate per copy
MUTATION_RATE_SCALE_EXPONENT = 3

# How many games each generation plays for eval
GAMES_PER_GEN = 1

# Default playback time accel (visual only)
# Use "." to increase, "," to decrease during playback
STEPS_PER_FRAME = 1

# Number of generations after which best model should be shown to user
SAMPLE_SHOW_GENERATION_STEP = 10


def play_game(model, device="cpu"):
    """
    Let the given model play the game and return the score
    """
    state = flappy.get_initial_state()

    steps = 0
    last_state = None
    while True:
        pressed = get_input(model, state, device)
        state = flappy.propagate(state, pressed)
        if state is None:
            break
        steps += 1
        last_state = state
        if steps > 99999:
            break
    return steps - abs(last_state["next_height"] - last_state["height"])


class NeuralNetwork(nn.Module):
    """
    A simple Neural Network with 5 inputs and 2 outputs
    """

    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(5, 10),
            nn.ReLU(),
            nn.Linear(10, 10),
            nn.ReLU(),
            nn.Linear(10, 2),
        )
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(5, 7),
            nn.ReLU(),
            nn.Linear(7, 2),
        )

    def forward(self, x):
        logits = self.linear_relu_stack(x)
        return logits

    def evaluate(self, x):
        """
        Take a state tensor and return a tensor indicating whether button is pressed
        """
        logits = self(x)
        pred_probab = nn.Softmax(dim=-1)(logits)
        return pred_probab.argmax(0)


def get_input(model, state, device="cpu"):
    """
    Take state dict and return a bool indicating whether button is pressed
    """
    X = torch.FloatTensor(list(state.values())[:5]).to(device)
    # print(X)
    logits = model.evaluate(X)
    # print(logits)
    return logits.item()

def do_training(child_method="cloning", max_generations=20, mutation_rate=0.2, generation_callback=None):
    device = "cpu"

    # Generate the number of models comprising one generation
    models = [NeuralNetwork().to(device) for _ in range(KEEP_BEST * CHILD_PER_BEST)]

    generation_scores = []

    for generation in range(max_generations):
        ratings = []
        print(f"Running {KEEP_BEST * CHILD_PER_BEST} Models of generation {generation}")

        # Generate fixed seeds for each play of this generation
        # Ensures each model plays same env so one can't get lucky
        seed = time.time()
        game_seeds = [random.random() for _ in range(GAMES_PER_GEN)]

        for i, model in enumerate(models):
            steps = 0
            for seed in game_seeds:
                random.seed(seed)
                steps += play_game(model, device)

            # Store score and model weights for this model
            ratings.append((steps, model.state_dict()))

        print("Done")

        # Sort models by score
        ratings = sorted(ratings, key=lambda tup: tup[0])

        # Get top KEEP_BEST models
        best = ratings[-KEEP_BEST:]

        generation_scores.append(best[-1][0])

        print("")
        print(f"Score of generation {generation}:")
        for b in ratings[:4]:
            print(f"{b[0]:12.3f} (avg = {b[0] / GAMES_PER_GEN:12.3f})")
        print("...")
        for b in best:
            print(f"{b[0]:12.3f} (avg = {b[0] / GAMES_PER_GEN:12.3f})")

        if generation_callback is not None:
            generation_callback(generation, models, ratings, game_seeds, device)

        # Generate children from the best models
        if child_method == "cloning":
            # Creates CHILD_PER_BEST copies of each of the best models
            for i, m in enumerate(models):
                parent = best[i // CHILD_PER_BEST]
                m.load_state_dict(parent[1])
        elif child_method == "crossover_pick":
            # Creates children which randomly contain values from one of their 2 parents
            for i, m in enumerate(models):
                parent1 = random.choice(best)[1]
                parent2 = random.choice(best)[1]
                child = parent1.copy()
                for key in child:
                    if random.random() > 0.5:
                        child[key] = parent2[key]
                m.load_state_dict(child)
        elif child_method == "crossover_avg":
            # Create children whose weights are the average of their 2 parents
            for i, m in enumerate(models):
                parent1 = random.choice(best)[1]
                parent2 = random.choice(best)[1]
                child = parent1.copy()
                for key in child:
                    if random.random() > 0.5:
                        child[key] = (parent1[key] + parent2[key]) / 2
                m.load_state_dict(child)
        else:
            print("Invalid crossover method!")
            exit()


        # Mutate children for next run
        for i, model in enumerate(models):
            # For each child, calculate a number from 0 to 1 and exp MUTATION_RATE_SCALE_EXPONENT
            # Ensures small mutation for most children but some children with high mutation
            model_scale = (
                (i % CHILD_PER_BEST) / CHILD_PER_BEST
            ) ** MUTATION_RATE_SCALE_EXPONENT

            for param in model.parameters():
                # Alter weights with normal distribution random numbers
                param.data += mutation_rate * model_scale * torch.randn_like(param)
    return generation_scores

if __name__ == "__main__":
    g = gui.GUI()

    def generation_callback(generation, models, ratings, seeds, device):
        model = models[0]
        model.load_state_dict(ratings[-1][1])
        seed = seeds[0]
        # Check if this generation should be shown to user:
        if generation % SAMPLE_SHOW_GENERATION_STEP == 0:
            print("Showing best model")
            random.seed(seed)

            state = flappy.get_initial_state()

            frame = 0
            # Game steps to do per frame shown (time acceleration)
            steps_per_frame = STEPS_PER_FRAME

            while True:
                events = g.get_events()
                if events is None:
                    # User pressed close button
                    # Skip display and continue training
                    break
                for e in events:
                    if e.type == pygame.KEYDOWN:
                        if e.unicode == ".":
                            steps_per_frame += 1
                        if e.unicode == ",":
                            steps_per_frame -= 1
                        print(f"Time accel: {steps_per_frame}")
                    steps_per_frame = max(1, steps_per_frame)

                # Do steps_per_frame steps
                for i in range(steps_per_frame):
                    pressed = get_input(model, state, device)
                    state = flappy.propagate(state, pressed)
                    frame += 1
                    if state is None:
                        # Game ended
                        break
                if state is None:
                    break
                g.draw_state(state, frame)
            print("Done")

    do_training(child_method=CHILD_METHOD, max_generations=MAX_GENERATIONS, mutation_rate=MUTATION_RATE, generation_callback=generation_callback)