import numpy as np


def get_random_moves(num_moves: int, random_seed: int = None):
    if random_seed:
        np.random.seed(random_seed)

    faces = {"L", "F", "R", "D", "U", "B"}
    counts = ["", "2"]
    inversions = ["", "'"]

    commands, last_face = [], ""
    for _ in range(num_moves):
        # we make sure not to repeat the same face in consecutive moves
        face = np.random.choice(sorted(faces.difference(last_face)))
        count = np.random.choice(counts)
        inverted = np.random.choice(inversions)
        commands.append(f"{face}{count}{inverted}")
        last_face = face

    return commands


def invert_move(move: str):
    if move.endswith("'"):
        return move[:-1]
    return move + "'"


def get_random_resolving_moves(num_moves: int, random_seed: int = None):
    commands = get_random_moves(num_moves=num_moves, random_seed=random_seed)
    commands = commands + list(reversed([invert_move(c) for c in commands]))
    return commands
