# PIN with diameter 25.00 +- 0.05 mm is accepted
#Pin within 0.1 mm is sent for rework.
#Any other pin is rejected.
#System reports ----> how many pins fell into each category and where the first rejected pin was found

diameter = float(input("Enter the diameter of the pin : "))
if 25.00 < diameter <= 25.05:
    print("Accepted")
elif 25.05 < diameter <= 25.10:
    print("Need for rework")
else:
    print("rejected")