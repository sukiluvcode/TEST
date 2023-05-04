def ordinary(i):
    print(i)

def yie(ls):
    i = 0
    while i < len(ls):
        yield ls[i]
        i += 1

ls = [1, 2]
for i in ls:
    ordinary(i)

print("separation")

for i in yie(ls):
    print(i)