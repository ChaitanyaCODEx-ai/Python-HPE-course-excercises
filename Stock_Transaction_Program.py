"""
Number of Shares that Joe purchased was 2000
when Joe purchased the stock, he paid 40 dollars per share
Joe paid his stockbroker a commission that amounted to 3 percent of the amount he paid for the stock

Two weeks later, Joe sold the stock. Here are the details of the sale:
The number of shares that Joe sold was 2000
He sold the stock for $42.75 per share
He paid his stockbroker another commision that amounted to 3 percent of the amount he recieved for the stock

Program:
1. The amount of money Joe paid for the stock.
2. The amount of commission Joe paid his broker when he bought the stock
3. The amount for which Joe sold the stock.
The ammount of commision Joe paid his broker when he sold the stock
Display the amount of money that Joe had left when he sold the stock and paid hi broker
(both times). If this amount is positive then Joe made a profit. If the amount is negative then joe lost money"""

stock_purchased = int(input("How much Stock Joe purchased : "))
total = stock_purchased*40
print("The amount of money Joe paid for the stock is : ",total)
print("The amount of money Joe paid to his stock broker : ",0.03*total)
print("\n\nTwo weeks later")
total2 = stock_purchased*42.75
print(f"The numebr of shares Joe sold was {stock_purchased}")
print("Joe sold his stock for $42.75 per share and a total of : ",42.75*stock_purchased)
print("The amount of money for another commision to his stockbroker : ",0.03*total2)
print("\n")
Moneyleft = (total2 - 0.03*total2) - (total - 0.03*total)
print("MONEY LEFT WITH JOE = ",Moneyleft)
if Moneyleft > 0:
    print("Joe made Profit")
else:
    print("joe is in loss")
