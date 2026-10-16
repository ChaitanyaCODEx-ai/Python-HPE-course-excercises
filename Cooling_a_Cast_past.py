furnace_temp = 900
workshop_temp = 30
Target_temp = 100
minute = 0
print("Your Furnace temperature is 900 degree C\nYour workshop temperature is 30 degree C")
while furnace_temp > Target_temp:
    furnace_temp -= (furnace_temp - workshop_temp)*0.08
    minute += 1
print("Minutes take to reach 100 degree celcius",minute," degree C")