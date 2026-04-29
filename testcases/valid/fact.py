n = 29
isPrime = True

if n <= 1:
    isPrime = False
else:
    i = 2

    while i * i <= n:
        if n / i * i == n:
            isPrime = False
            break

        i = i + 1

print("Is prime:")
print(isPrime)