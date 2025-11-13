def move_one_ball(arr):
    if not arr:
        return True

    n = len(arr)
    sorted_arr = sorted(arr)

    for i in range(n):
        # Perform a right shift 'i' times
        # This is equivalent to checking if the original array is a rotation of the sorted array
        is_match = True
        for j in range(n):
            if arr[j] != sorted_arr[(j + i) % n]:
                is_match = False
                break
        if is_match:
            return True

    return False