def count_nums(arr):
    def digit_sum(n):
        return sum(int(d) if n >= 0 else -int(d) for d in str(abs(n)))
    
    return sum(1 for num in arr if digit_sum(num) > 0)