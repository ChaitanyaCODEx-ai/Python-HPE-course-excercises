import time
n = int(input("How many students ? "))
marks = list(range(n))
start = time.perf_counter()
pairs_checked = 0
for first in range(n):
    for second in range(first + 1,n):
        if marks[first] == marks[second]:
            print("Same marks found")
        pairs_checked = pairs_checked + 1
end = time.perf_counter()
print("pairs checked: ", pairs_checked)
print("Time taken: ", (end - start)*1000, "ms")