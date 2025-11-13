def words_string(s):
    return [word.strip() for word in s.replace(',', ' ').split()]

# Test cases
print(words_string("Hi, my name is John"))  # ["Hi", "my", "name", "is", "John"]
print(words_string("One, two, three, four, five, six"))  # ["One", "two", "three", "four", "five", "six"]
print(words_string("Hello,world"))  # ["Hello", "world"]
print(words_string("  spaced   words  "))  # ["spaced", "words"]
print(words_string("A,B,C,D,E"))  # ["A", "B", "C", "D", "E"]