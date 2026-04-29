numbers = [10, 20, 30]

numbers.append(40)
numbers.append(50)

total = 0

for i in range(len(numbers)):
    total = total + numbers[i]

print("List sum:")
print(total)

numbers[0] = 100

print("Updated first value:")
print(numbers[0])