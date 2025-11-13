def minSubArraySum(nums):
    """
    Given an array of integers nums, find the minimum sum of any non-empty sub-array
    of nums.
    Example
    minSubArraySum([2, 3, 4, 1, 2, 4]) == 1
    minSubArraySum([-1, -2, -3]) == -6
    """
    min_so_far = float('inf')
    current_min = 0

    for x in nums:
        current_min += x
        if current_min < min_so_far:
            min_so_far = current_min
        if current_min > 0:  # If current_min becomes positive, it's better to start a new subarray
            current_min = 0
            
    # Edge case: if all numbers are positive, current_min will reset to 0
    # and min_so_far will be the smallest single positive number.
    # This is handled by initializing min_so_far to float('inf') and
    # current_min to 0. If all numbers are positive, current_min will
    # never go below 0 after the first element, and min_so_far will
    # correctly capture the smallest single element (which is the min subarray sum).
    # However, the standard Kadane's for minimum sum needs a slight adjustment
    # if all numbers are positive.
    # Let's re-evaluate Kadane's for minimum sum.

    # Correct Kadane's for minimum sum:
    # Initialize min_ending_here to a large positive number (or the first element)
    # Initialize min_so_far to a large positive number (or the first element)

    min_ending_here = nums[0]
    min_so_far = nums[0]

    for i in range(1, len(nums)):
        min_ending_here = min(nums[i], min_ending_here + nums[i])
        min_so_far = min(min_so_far, min_ending_here)

    return min_so_far