import random
import settings


def get_height(rand_gen=None):
    """
    Generate a gap height inside the span specified in the settings
    """
    if rand_gen:
        rand = rand_gen.random()
    else:
        rand = random.random()
    return 0.5 * (1 - settings.gate_span) + settings.gate_span * rand


def get_initial_state(rand_gen=None):
    """
    Return game state for start of game
    """
    return {
        "height": 0.5,
        "speed": settings.start_speed,
        "vert_vel": 0,
        "next_dist": 1,
        "next_height": get_height(rand_gen=rand_gen),
        "frame": 0,
        "last_input": -1,
    }


def propagate(state, pressed, rand_gen=None):
    """
    Take the previous game state and a bool indicating whether up button
    is pressed and return the next game state. Return None if game ended.
    """
    state["frame"] += 1

    # If last input was recent, block button
    if (
        state["last_input"] is not None
        and state["frame"] < state["last_input"] + settings.input_cooldown
    ):
        pressed = False

    # Apply gravity to vertical velocity
    state["vert_vel"] -= settings.gravity

    # If up button is pressed, set constant up velocity
    if pressed:
        state["last_input"] = state["frame"]
        state["vert_vel"] = settings.up_accel

    # Apply vertical speed
    state["height"] += state["vert_vel"]

    # Move pipe closer to bird
    state["next_dist"] -= state["speed"]

    # Increase speed
    state["speed"] += settings.speed_increment

    # End game if hitting floor or ceiling
    if not (0 <= state["height"] <= 1):
        return None

    # If bird is currently in gap between pipes
    if state["next_dist"] <= settings.pipe_width:
        # If bird is intersecting pipe, end game
        if (state["height"] < state["next_height"] - (settings.gap_height / 2)) or (
            state["height"] > state["next_height"] + (settings.gap_height / 2)
        ):
            return None

        # If bird has passed current pipe, generate a new one in the distance
        if state["next_dist"] <= 0:
            state["next_dist"] = 1
            state["next_height"] = get_height(rand_gen=rand_gen)

    return state
