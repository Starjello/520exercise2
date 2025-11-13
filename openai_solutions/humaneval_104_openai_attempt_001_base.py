def unique_digits(x):
    def has_even_digit(n):
        return any(int(d) % 2 == 0 for d in str(n))
    
    result = [num for num in x if not has_even_digit(num)]
    return sorted(result)