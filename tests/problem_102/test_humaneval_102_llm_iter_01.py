# Auto-import solution module from file path
import importlib.util, pathlib
_SOL_FILE = pathlib.Path(r"""C:/Users/Alexander_Bennett/OneDrive - UMass Lowell/Desktop/llm-eval/openai_solutions/humaneval_102_openai_attempt_001_base.py""")
_spec = importlib.util.spec_from_file_location("solution_mod", _SOL_FILE)
solution_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(solution_mod)
choose_num = getattr(solution_mod, "choose_num")

# Auto-import solution module from file path
import importlib.util, pathlib
_SOL_FILE = pathlib.Path(r"""C:/Users/Alexander_Bennett/OneDrive - UMass Lowell/Desktop/llm-eval/openai_solutions/humaneval_102_openai_attempt_001_base.py""")
_spec = importlib.util.spec_from_file_location("solution_mod", _SOL_FILE)
solution_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(solution_mod)
choose_num = getattr(solution_mod, "choose_num")

def test_choose_num():
    # Test case where x is even and y is odd, with a gap in between
    assert choose_num(2, 5) == 4
    
    # Test case where x is odd and y is even, with a gap in between
    assert choose_num(3, 6) == 6
    
    # Test case where x and y are both even but y is less than x
    assert choose_num(12, 10) == -1
    
    # Test case where x is odd and y is odd, with no even numbers in range
    assert choose_num(17, 19) == -1
    
    # Test case where x is even and y is even, with no even numbers in range
    assert choose_num(10, 10) == 10  # Already covered, but testing boundary
    
    # Test case where x is very large and y is very large but odd
    assert choose_num(999999999, 1000000001) == -1
    
    # Test case where x is very large and y is very large but even
    assert choose_num(1000000000, 1000000002) == 1000000002
    
    # Test case where x is odd and y is even, with a large gap
    assert choose_num(1000001, 1000005) == 1000004
    
    # Test case where x is even and y is odd, with a large gap
    assert choose_num(1000000, 1000003) == 1000002
    
    # Test case where x and y are equal and both are the maximum positive integer
    assert choose_num(2147483647, 2147483647) == -1  # Assuming 32-bit integer limit
    
    # Test case where x is less than y and both are the minimum positive integers
    assert choose_num(1, 2) == 2  # Already covered, but testing boundary
    
    # Test case where x is negative and y is positive, testing behavior
    assert choose_num(-1, 1) == 0  # Not valid as per spec but testing behavior
    
    # Test case where x is positive and y is negative, testing behavior
    assert choose_num(1, -1) == -1  # Not valid as per spec but testing behavior

    # Test case where x is even and y is odd, with x being the smallest even number
    assert choose_num(2, 3) == 2

    # Test case where x is odd and y is even, with x being the smallest odd number
    assert choose_num(1, 2) == 2

    # Test case where x and y are both odd and y is just one greater than x
    assert choose_num(21, 22) == 22

    # Test case where x and y are both even and y is just one greater than x
    assert choose_num(20, 21) == 20

    # Test case where x is even and y is even, with no even numbers in range
    assert choose_num(10, 11) == 10  # Testing boundary with no valid even number

    # Test case where x is odd and y is odd, with a large gap
    assert choose_num(101, 199) == 198  # Testing larger range with odd bounds

    # Test case where x is greater than y, testing early return
    assert choose_num(5, 3) == -1

    # Test case where x and y are both even and equal to 0
    assert choose_num(0, 0) == 0  # Testing boundary with zero

    # Test case where x is 0 and y is a positive even number
    assert choose_num(0, 4) == 4  # Testing boundary with zero as lower bound

    # Test case where x is a positive odd number and y is a positive even number
    assert choose_num(5, 6) == 6  # Testing boundary with odd lower bound
