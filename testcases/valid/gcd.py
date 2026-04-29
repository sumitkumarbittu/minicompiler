def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

x = 5
result = factorial(x)

print("Factorial result:")
print(result)