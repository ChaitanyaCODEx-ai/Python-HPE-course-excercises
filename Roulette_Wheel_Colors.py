"""ON a roulette wheel the pockets are numbered from 0 to 36. The colors of the wheel are as follows"""
response = int(input("Enter your pocket number : "))
if response == 0:
    print(f"Your Pocket {response} is green")
elif 0 < response < 11:
    if response%2 == 0:
        print(f"Pocket {response} is black")
    else:
        print(f"Pocket {response} is red")
elif 10<response<19:
    if response%2==0:
        print(f"Pocket {response} is red")
    else:
        print(f"Pocket {response} is black")
elif 18<response<29:
    if response%2==0:
        print(f"Pocket {response} is black")
    else:
        print(f"Pocket {response} is red")
elif 28<response<37:
    if response%2==0:
        print(f"Pocket {response} is red")
    else:
        print(f"Pocket {response} is black")
else:
    print("ERROR!!!!")