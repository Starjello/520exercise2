def count_nums(arr):
    """
    Write a function count_nums which takes an array of integers and returns
    the number of elements which has a sum of digits > 0.
    If a number is negative, then its first signed digit will be negative:
    e.g. -123 has signed digits -1, 2, and 3.
    >>> count_nums([]) == 0
    >>> count_nums([-1, 11, -11]) == 1
    >>> count_nums([1, 1, 2]) == 3
    >>> count_nums([-10, -11, -12]) == 0
    >>> count_nums([10, 20, 30]) == 3
    >>> count_nums([-1, -2, -3, -4, -5, -6, -7, -8, -9]) == 0
    >>> count_nums([1, 2, 3, 4, 5, 6, 7, 8, 9]) == 9
    >>> count_nums([-100, -200, -300]) == 0
    >>> count_nums([100, 200, 300]) == 3
    >>> count_nums([-123, 456, -789]) == 1
    >>> count_nums([0]) == 1
    >>> count_nums([-5]) == 0
    >>> count_nums([5]) == 1
    >>> count_nums([-12]) == 0
    >>> count_nums([12]) == 1
    >>> count_nums([-10]) == 0
    >>> count_nums([10]) == 1
    >>> count_nums([-99]) == 0
    >>> count_nums([99]) == 1
    >>> count_nums([-1000]) == 0
    >>> count_nums([1000]) == 1
    """
    count = 0
    for num in arr:
        s = str(num)
        digit_sum = 0
        if s[0] == '-':
            digit_sum += -int(s[1])
            for digit_char in s[2:]:
                digit_sum += int(digit_char)
        else:
            for digit_char in s:
                digit_sum += int(digit_char)
        
        if digit_sum > 0:
            count += 1
    return count