def reverse_delete(s, c):
    """Task
    We are given two strings s and c, you have to deleted all the characters in s that are equal to any character in c
    then check if the result string is palindrome.
    A string is called palindrome if it reads the same backward as forward.
    You should return a tuple containing the result string and True/False for the check.
    Example
    For s = "abcde", c = "ae", the result should be ('bcd',False)
    For s = "abcdef", c = "b"  the result should be ('acdef',False)
    For s = "abcdedcba", c = "ab", the result should be ('cdedc',True)
    """
    c_set = set(c)
    result_s_list = []
    for char_s in s:
        if char_s not in c_set:
            result_s_list.append(char_s)
    
    result_s = "".join(result_s_list)
    
    is_palindrome = (result_s == result_s[::-1])
    
    return (result_s, is_palindrome)