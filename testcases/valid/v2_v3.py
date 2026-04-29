a = True
b = False
print(a and not b)

x = 3.5
y = 2
print(x + y)

name = "MiniPython"
print(name)
print(name == "MiniPython")

total = 0
for i in range(1, 5):
    if i == 3:
        continue
    total = total + i
print(total)

xs = [1, 2, 3]
xs.append(4)
xs[0] = 10
print(xs[0] + xs[3])
print(len(xs))

while True:
    pass
    break
