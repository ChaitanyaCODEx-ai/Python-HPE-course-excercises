#Display the series 1,3,5,7...............,29
for i in range(1,30,2): #-----------> step = 2 opening at 1 closing at 30
    print (i,end='   ')

#DISPLAY THE SERIES 2,4,6,8,..................30
print("\n")
print("="*100)
for i in range(2,30,2):
    print(i,end='   ')

# Countdown from 100 to 0
print("\n")
print("="*100)
for i in range(100,-1,-10):
    print(i,end='   ')

#Alternating sum 1-2+3-4+......-20
print("\n")
print("="*100)
t = 0
for a in range(1,21):
    if a%2==0:
        t -= a
    else:
        t += a
print("THE SOLUTION OF THE SERIES IS", t)

a = range(1,100,10)
for i in a:
    if i%7==0:
        print(i)
        continue
    else:
        pass

val = [2,3,4,5,78,90]
flag = False
n = int(input('Enter any num :'))
for i in val:
    if i == n:
        flag = True
        break
if flag == True:
    print("Found")
else:
    print("Not Found!!!!")