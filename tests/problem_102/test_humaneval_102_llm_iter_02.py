# Auto-import solution module from file path
import importlib.util, pathlib
_SOL_FILE = pathlib.Path(r"""C:/Users/Alexander_Bennett/OneDrive - UMass Lowell/Desktop/llm-eval/openai_solutions/humaneval_102_openai_attempt_001_base.py""")
_spec = importlib.util.spec_from_file_location("solution_mod", _SOL_FILE)
solution_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(solution_mod)
choose_num = getattr(solution_mod, "choose_num")

def test_choose_num():
    # Test case where x is less than y and both are even
    assert choose_num(4, 10) == 10  # Testing range with multiple evens

    # Test case where x is less than y and both are odd
    assert choose_num(5, 11) == 10  # Testing range with multiple evens

    # Test case where x is equal to y and both are odd
    assert choose_num(7, 7) == -1  # Testing boundary with no valid even number

    # Test case where x is equal to y and both are even
    assert choose_num(8, 8) == 8  # Testing boundary with valid even number

    # Test case where x is negative and y is positive, testing behavior
    assert choose_num(-5, 5) == 4  # Testing range with negative lower bound

    # Test case where x is positive and y is negative, testing behavior
    assert choose_num(5, -5) == -1  # Testing range with positive lower bound

    # Test case where x is 0 and y is a positive odd number
    assert choose_num(0, 3) == 2  # Testing boundary with zero as lower bound

    # Test case where x is a positive odd number and y is a positive odd number
    assert choose_num(9, 15) == 14  # Testing range with odd bounds

    # Test case where x is a large even number and y is a large odd number
    assert choose_num(1000000000, 1000000001) == 1000000000  # Testing large range

    # Test case where x is a large odd number and y is a large even number
    assert choose_num(999999999, 1000000000) == 1000000000  # Testing large range

    # Test case where x is even and y is odd, with x being the smallest even number
    assert choose_num(2, 4) == 4  # Testing small range with valid even number

    # Test case where x is odd and y is even, with x being the smallest odd number
    assert choose_num(1, 3) == 2  # Testing small range with valid even number

    # Test case where x is even and y is odd, with no even numbers in range
    assert choose_num(3, 5) == -1  # Testing range with no valid even number

    # Test case where x is odd and y is even, with no even numbers in range
    assert choose_num(5, 7) == -1  # Testing range with no valid even number
