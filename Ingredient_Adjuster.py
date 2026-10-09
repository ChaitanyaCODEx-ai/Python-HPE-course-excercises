ask = input("Do you want to make a cookie : (y/n)")
if ask == "y":
    cookie = int(input("How many cookies you want to produce : "))
    Number_of_cups_of_Sugar = (1.5/48)*cookie
    Number_of_cups_of_Butter = (1/48)*cookie
    Number_of_cups_of_flour = (2.75/48)*cookie
    print(f"So the required Items are: \nCups of sugar:{Number_of_cups_of_Sugar}\nCups of Butter: {Number_of_cups_of_Butter}\nCups of Flour : {Number_of_cups_of_flour}\nYou are now able to make {cookie} cookies")
elif ask == "n":
    print("You dont want to make a cookie")
else:
    print("Invalid Input")