def is_nested(string):
    stack = []
    max_depth = 0
    current_depth = 0

    for char in string:
        if char == '[':
            stack.append(char)
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        elif char == ']':
            if stack and stack[-1] == '[':
                stack.pop()
                current_depth -= 1
            else:
                # Mismatched closing bracket, reset depth as it's not a valid nesting path
                # for the current sequence. We still want to track max_depth from valid parts.
                current_depth = 0 
                stack = [] # Clear stack to start fresh for potential new valid sequences
    
    return max_depth >= 2