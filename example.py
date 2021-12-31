# I want to print out people's ages

age = 22
print(f"My age is {age}")
print(f"Nabaa's age is {age}")
print(f"Nabaa is {age - 18} years older than Furkan")

# NOT MUTUALLY EXCLUSIVE = IF age > 21 ALL of these will run
if age >= 21:
    print("You can drink")
if age >= 18:
    print("You can vote")
if age >= 17:
    print("You can drive")

# MUTUALLY EXCLUSIVE = ONLY ONE OF THESE WILL HAPPEN
grade = 80
ap = True
if grade >= 90 or ap:
    print("Your grade is an A")
elif 80 <= grade < 90:
    print("Your grade is a B")
elif 70 <= grade < 80:
    print("Your grade is a C")
else:
    print("You are a failure")