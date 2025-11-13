# Auto-import solution module from file path
import importlib.util, pathlib
_SOL_FILE = pathlib.Path(r"""C:/Users/Alexander_Bennett/OneDrive - UMass Lowell/Desktop/llm-eval/openai_solutions/humaneval_107_openai_attempt_001_base.py""")
_spec = importlib.util.spec_from_file_location("solution_mod", _SOL_FILE)
solution_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(solution_mod)
choose_num = getattr(solution_mod, "choose_num")

# Auto-import solution module from file path
import importlib.util, pathlib
_SOL_FILE = pathlib.Path(r"""C:/Users/Alexander_Bennett/OneDrive - UMass Lowell/Desktop/llm-eval/openai_solutions/humaneval_107_openai_attempt_001_base.py""")
_spec = importlib.util.spec_from_file_location("solution_mod", _SOL_FILE)
solution_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(solution_mod)
even_odd_palindrome = getattr(solution_mod, "even_odd_palindrome")

def test_even_odd_palindrome():
    # Test with the smallest valid input
    assert even_odd_palindrome(1) == (0, 1)  # Only 1 is odd

    # Test with the first even palindrome
    assert even_odd_palindrome(2) == (1, 1)  # 1 is odd, 2 is even

    # Test with a small range including both even and odd palindromes
    assert even_odd_palindrome(3) == (1, 2)  # 1, 2, 3 -> 1 even (2), 2 odd (1, 3)

    # Test with a range that includes more palindromes
    assert even_odd_palindrome(10) == (4, 6)  # 1-9 are palindromes, 2, 4, 6, 8 are even

    # Test with a range that includes all single-digit palindromes
    assert even_odd_palindrome(9) == (4, 5)  # 1-9 -> 4 even (2, 4, 6, 8), 5 odd (1, 3, 5, 7, 9)

    # Test with a larger range
    assert even_odd_palindrome(12) == (4, 6)  # 1-11 are palindromes, 2, 4, 6, 8 are even

    # Test with the maximum valid input
    assert even_odd_palindrome(1000) == (400, 600)  # 1-999 palindromes, even and odd counts

    # Test with a range that includes no even palindromes
    assert even_odd_palindrome(5) == (2, 3)  # 1-5 -> 2 even (2, 4), 3 odd (1, 3, 5)

    # Test with a range that includes only even palindromes
    assert even_odd_palindrome(8) == (4, 4)  # 1-8 -> 4 even (2, 4, 6, 8), 4 odd (1, 3, 5, 7)

    # Test with a range that includes only odd palindromes
    assert even_odd_palindrome(9) == (4, 5)  # 1-9 -> 4 even (2, 4, 6, 8), 5 odd (1, 3, 5, 7, 9)

    # Test with a range that includes no palindromes (invalid case, but for coverage)
    assert even_odd_palindrome(0) == (0, 0)  # No palindromes below 1

    # Test with a range that includes a single even palindrome
    assert even_odd_palindrome(4) == (2, 2)  # 1-4 -> 2 even (2, 4), 2 odd (1, 3)

    # Test with a range that includes a single odd palindrome
    assert even_odd_palindrome(7) == (3, 4)  # 1-7 -> 3 even (2, 4, 6), 4 odd (1, 3, 5, 7)

    # Test with a range that includes all two-digit palindromes
    assert even_odd_palindrome(99) == (36, 63)  # 1-99 -> 36 even, 63 odd palindromes

    # Test with a range that includes no palindromes (edge case)
    assert even_odd_palindrome(0) == (0, 0)  # No palindromes below 1

    # Test with a range that includes only two-digit palindromes
    assert even_odd_palindrome(22) == (10, 12)  # 1-22 -> 10 even (2, 4, 6, 8, 11, 22), 12 odd (1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21)

    # Test with a range that includes a large number of palindromes
    assert even_odd_palindrome(200) == (80, 120)  # 1-200 -> 80 even, 120 odd palindromes
