def by_length(arr):
    if not arr:
        return []
    
    valid_numbers = [num for num in arr if 1 <= num <= 9]
    valid_numbers.sort(reverse=True)
    
    number_names = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    return [number_names[num] for num in valid_numbers]