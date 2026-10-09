"""
ATTRIBUTE                 Value
Account ID                AC1025
Opening Balance           15000
Transaction Amount        4500
Account Status            active\

1.Identify a suitable data types for each attirbute
2.Assign the values to describe Python variables
3.Calculate the closing balance after a withdrawal
4. Display the account ID, opening balance, withdrawal and closing balance"""

#Excercise 1
Account_ID = "AC1025"
Opening_Balance = 15000
withdrawal_Amount = 16000
Account_Active = True

closing_balance = Opening_Balance - withdrawal_Amount
print("Account ID:",Account_ID)
print("Opening Balance: ",Opening_Balance)
print("withdrawal_Amount: ",withdrawal_Amount)
print("closing balanace ", closing_balance)

#EXCERCISE 2
amount_positive = withdrawal_Amount > 0
sufficient_funds = Opening_Balance >= withdrawal_Amount
valid_withdrawal = {
    amount_positive
    and sufficient_funds
    and Account_Active
}

print (amount_positive, sufficient_funds, Account_Active, valid_withdrawal)

#Excercise 3
print("\n")
"""Total_Debits = 24500
Total_Credits = 24500
print("Compare the total credits and total debits")
if Total_Credits > Total_Debits:
    print(Total_Debits<Total_Credits)
elif Total_Credits < Total_Debits:
    print(Total_Debits > Total_Credits)
else:
    print("Both credit and Debit are equal")

#After changing the Total credits to 24400
Total_Debits = 24500
Total_Credits = 24400
if Total_Credits > Total_Debits:
    print(Total_Debits<Total_Credits)
elif Total_Credits < Total_Debits:
    print(Total_Debits > Total_Credits)
else:
    print("Both credit and Debit are equal")"""

#From the above code we can establish that what is more than the other but it cannot establish the difference between them is by how much ...
total_debits = 24500
total_credits = 24500
ledger_balanced = total_debits == total_credits
print(ledger_balanced)
total_credits = 24400
ledger_balanced = total_debits > total_credits
print(ledger_balanced)