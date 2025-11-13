def even_odd_palindrome(n):
    even_palindromes = 0
    odd_palindromes = 0

    for i in range(1, n + 1):
        s = str(i)
        if s == s[::-1]:  # Check if it's a palindrome
            if i % 2 == 0:
                even_palindromes += 1
            else:
                odd_palindromes += 1

    return (even_palindromes, odd_palindromes)