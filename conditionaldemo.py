phy = input('Enter your PHYSICS Score : ')
chem =input('Enter your CHEMISTRY Score : ')
maths =input('Enter your MATHS Score : ')

total = phy + maths + chem
avg = int(total)/3
print('Total Score:',total)
print('Average Score: ',avg)
if avg >= 50:
    print('Pass')
else:
    print("YOU ARE A FALIURE !!!!!!!!!")