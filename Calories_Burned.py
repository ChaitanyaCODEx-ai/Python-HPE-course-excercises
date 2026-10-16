#Runnning on a particular treadmill you burn 4.2 calories per minute.
#Program that tells the number of calories burned after 10,15,20,25 and 30 minutes
print("Runnning on a particular treadmill you burn 4.2 calories per minute.")
minute = 0
while minute <= 30:
    print(f"Calories burned in {minute} min ", 4.2*minute)
    minute += 5