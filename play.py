import flappy

import gui


g = gui.GUI()

state = flappy.get_initial_state()
# Game loop.
i = 0
alive = True
while True:
    events = g.get_events()
    if events is None:
        break
    pressed = g.get_pressed()

    if i > 30:
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
