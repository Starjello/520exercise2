def is_palindrome(string: str) -> bool:
    """ Test if given string is a palindrome """
    return string == string[::-1]


def make_palindrome(string: str) -> str:
    """ Find the shortest palindrome that begins with a supplied string.
    Algorithm idea is simple:
    - Find the longest postfix of supplied string that is a palindrome.
    - Append to the end of the string reverse of a string prefix that comes before the palindromic suffix.
    >>> make_palindrome('')
    ''
    >>> make_palindrome('cat')
    'catac'
    >>> make_palindrome('cata')
    'catac'
    """
    if not string:
        return ""

    # Find the longest postfix of the supplied string that is a palindrome.
    longest_palindromic_suffix = ""
    for i in range(len(string)):
        suffix = string[i:]
        if is_palindrome(suffix):
            longest_palindromic_suffix = suffix
            break
    
    # The prefix that comes before the palindromic suffix.
    # This is string[:i] where i is the starting index of the longest_palindromic_suffix
    prefix_to_reverse = string[:len(string) - len(longest_palindromic_suffix)]

    # Append to the end of the string reverse of a string prefix that comes before the palindromic suffix.
    return string + prefix_to_reverse[::-1]