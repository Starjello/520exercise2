import math

def max_fill(grid, capacity):
    total_water = 0
    for row in grid:
        total_water += sum(row)
    
    if total_water == 0:
        return 0

    return math.ceil(total_water / capacity)