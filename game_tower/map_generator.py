import random

TILE_SIZE = 64

def generate_level4_path(width=50, height=50):
    path = []

    x, y = 0, 0
    path.append((x, y))

    while x < width - 1 or y < height - 1:
        if x == width - 1:
            y += 1
        elif y == height - 1:
            x += 1
        else:
            if random.random() < 0.5:
                x += 1
            else:
                y += 1
        path.append((x, y))

    return path
