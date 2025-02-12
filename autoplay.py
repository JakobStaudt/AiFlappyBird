import flappy
import torch
import gui
from train import NeuralNetwork, get_input

g = gui.GUI()

state = flappy.get_initial_state()

with open("highscore.dat", "rb") as f:
    statedict = torch.load(f)

model = NeuralNetwork()
model.load_state_dict(statedict)

# Game loop.
i = 0
alive = True
while True:
    events = g.get_events()
    if events is None:
        break

    if i > 30:
        pressed = get_input(model, state)
        if alive:
            new_state = flappy.propagate(state, pressed)
            if new_state is not None:
                state = new_state
            else:
                alive = False
        else:
            if pressed:
                break

    i += 1

    g.draw_state(state)
