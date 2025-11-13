from openai_solutions.humaneval_102_openai_attempt_001_base import choose_num

def test_x_greater_than_y():
    assert choose_num(5, 3) == -1

def test_even_in_range():
    assert choose_num(3, 5) == 4

def test_no_even_in_range():
    assert choose_num(3, 3) == -1

def test_single_even():
    assert choose_num(2, 2) == 2
