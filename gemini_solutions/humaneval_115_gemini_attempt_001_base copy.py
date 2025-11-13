import math

def max_fill(grid, capacity):
    """
    You are given a rectangular grid of wells. Each row represents a single well,
    and each 1 in a row represents a single unit of water.
    Each well has a corresponding bucket that can be used to extract water from it, 
    and all buckets have the same capacity.
    Your task is to use the buckets to empty the wells.
    Output the number of times you need to lower the buckets.
    """
    total_lowers = 0
    for well in grid:
        water_in_well = sum(well)
        lowers_for_well = math.ceil(water_in_well / capacity)
        total_lowers += lowers_for_well
    return total_lowers