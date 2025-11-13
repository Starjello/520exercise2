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
    # Test case where x is less than y and both are even, testing multiple evens
    assert choose_num(2, 8) == 8

    # Test case where x is less than y and both are odd, testing multiple evens
    assert choose_num(3, 9) == 8

    # Test case where x is equal to y and both are odd, testing boundary with no valid even number
    assert choose_num(15, 15) == -1

    # Test case where x is equal to y and both are even, testing boundary with valid even number
    assert choose_num(16, 16) == 16

    # Test case where x is negative and y is positive, testing behavior with negative lower bound
    assert choose_num(-10, 10) == 10

    # Test case where x is positive and y is negative, testing behavior with positive lower bound
    assert choose_num(10, -10) == -1

    # Test case where x is 0 and y is a positive odd number, testing boundary with zero as lower bound
    assert choose_num(0, 5) == 4

    # Test case where x is a positive odd number and y is a positive odd number, testing range with odd bounds
    assert choose_num(11, 19) == 18

    # Test case where x is a large even number and y is a large odd number, testing large range
    assert choose_num(1000000002, 1000000003) == 1000000002

    # Test case where x is a large odd number and y is a large even number, testing large range
    assert choose_num(999999998, 1000000000) == 1000000000

    # Test case where x is even and y is odd, with x being the smallest even number
    assert choose_num(2, 3) == 2

    # Test case where x is odd and y is even, with x being the smallest odd number
    assert choose_num(1, 4) == 4

    # Test case where x and y are both odd and y is just one greater than x
    assert choose_num(21, 22) == 22

    # Test case where x and y are both even and y is just one greater than x
    assert choose_num(20, 21) == 20

    # Test case where x is even and y is even, with no even numbers in range
    assert choose_num(10, 11) == 10

    # Test case where x is greater than y, testing early return
    assert choose_num(5, 3) == -1

    # Test case where x and y are both even and equal to 0
    assert choose_num(0, 0) == 0

    # Test case where x is 0 and y is a positive even number
    assert choose_num(0, 4) == 4

    # Test case where x is a positive odd number and y is a positive even number
    assert choose_num(5, 6) == 6
