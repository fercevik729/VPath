# boolean variable
overweight = True
athletic = True

# Example
if not overweight or athletic:
    # If you are either not overweight or/both athletic, you can run
    print("You can run")
if not overweight and athletic:
    # If you are not overweight AND athletic you can sprint
    print("YOU CAN SPRINT")
else:
    # Otherwise you can't do nothing
    print("You can't")

# Practice problems
# Answer choices: boolean, integer, float, and string
a = True # What kind of variable is this?
b = 2.5 # What kind of variable is this?
c = "Nabaa" # What kind of variable is this?
d = 17 # What kind of variable is this?

# Sets, lists, dictionaries, and tuples
# Data structure in python: can contain multiple values of potentially different types

# Lists:
# # They are mutable or changeable
# # They are slice able
ages = [1, 2, 3, 4.99, '5', 6]
print(f"Before: {ages}")
ages.append(17)
print(f"After: {ages}")

print(f"Before popping: {ages}")
baby = ages.pop(0)
print(f"After popping: {ages}")
print(f"Baby age: {baby}")

print(f"The fourth element of ages is: {ages[3]}")
print(f"The first 3 elements of ages are: {ages[:3]}")
print(f"The last element of ages is: {ages[-1]}")

# Go over every single age in ages and prints the double of the age
for age in ages:
    # If age is an instance of a float object or decimal number, round it and then double it
    if isinstance(age, float):
        print(round(age) * 2)
    # Otherwise just cast it or convert it to int
    else:
        print(int(age) * 2)

squares = [x * x for x in range(1, 11)]
print(squares)
