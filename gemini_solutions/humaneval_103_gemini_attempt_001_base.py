def rounded_avg(n, m):
    """You are given two positive integers n and m, and your task is to compute the
    average of the integers from n through m (including n and m). 
    Round the answer to the nearest integer and convert that to binary.
    If n is greater than m, return -1.
    Example:
    rounded_avg(1, 5) => "0b11"
    rounded_avg(7, 5) => -1
    rounded_avg(10, 20) => "0b1111"
    rounded_avg(20, 33) => "0b11010"
    """
    if n > m:
        return -1
    
    # Calculate the sum of integers from n to m
    # The sum of an arithmetic series is (number of terms / 2) * (first term + last term)
    # Number of terms = m - n + 1
    sum_val = (m - n + 1) * (n + m) / 2
    
    # Calculate the average
    average = sum_val / (m - n + 1)
    
    # Round the average to the nearest integer
    rounded_average = round(average)
    
    # Convert the rounded average to binary
    return bin(rounded_average)