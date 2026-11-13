'''n = int(input("Enter n : "))
def factorial(n):
    """Calculate the factorial of a non-negative integer n."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    if n == 0 or n == 1:
        return 1
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def print_factorial_table():
    for i in range(0,n+1):
        print(i,"!              = ",factorial(i))

print_factorial_table()'''

'''def power(base,exponent):
    if exponent == 0:
        return 1
    
    return base*power(base,exponent-1)

print(power(9,2))'''

# PIN GUESSER
n = int(input("Enter your 4 digit pin : "))
print("PIN REGISTERED !!")
yn = input(("DO YOU WANT TO OPEN YOUR SAFE (y/n)"))
if yn == "y":
    print("Go ahead and put the pin")
elif yn == "n":
    print("You dont want to enter the pin")
else:
    print("INVALID INPUT ANSWER ONLY IN y OR n")

def pin(n,chances):
    guess = int(input(f"Enter your PIN ({chances} chances left): "))
    if n == guess:
        return "Safe unlocked"
    print("INCORRECT!, Try again")
    if chances <= 0:
        return "Safe locked for temporary time"
    return pin(n,chances - 1)

print(pin(n,3))