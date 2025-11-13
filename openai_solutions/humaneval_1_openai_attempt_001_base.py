from typing import List

def separate_paren_groups(paren_string: str) -> List[str]:
    paren_string = paren_string.replace(" ", "")
    result = []
    count = 0
    current_group = []
    
    for char in paren_string:
        if char == '(':
            if count == 0 and current_group:
                result.append(''.join(current_group))
                current_group = []
            current_group.append(char)
            count += 1
        elif char == ')':
            current_group.append(char)
            count -= 1
            if count == 0:
                result.append(''.join(current_group))
                current_group = []
    
    return result

# Test cases
print(separate_paren_groups('( ) (( )) (( )( ))'))  # ['()', '(())', '(()())']
print(separate_paren_groups('() (()) (()())'))  # ['()', '(())', '(()())']
print(separate_paren_groups('(( )) ( )'))  # ['(())', '()']
print(separate_paren_groups('()'))  # ['()']
print(separate_paren_groups(''))  # []