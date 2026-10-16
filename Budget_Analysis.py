"""budget = int(input("Tell me your budget for a month : "))
answer = input("Do you want to see your budget (yes/no)")
count = 1
answer = "yes"
total = 0
while answer == "yes":
    expenses = int(input(f"TELL me your expense {count} : "))
    answer = input("Do you have any more expenses ? : (yes/no)")
    count += 1
    total += expenses
print(total, "it is the total expense")
if budget - total > 0:
    print("You are under your budget by ", budget - total)
else:
    print("You are over budget by ", abs(budget - total))"""

"""
# Initialize budget and collection lists
budget = int(input("Tell me your budget for a month: "))
expenses_list = []

# Collect expenses in a loop
count = 1
answer = "yes"
while answer == "yes":
    expense_name = input(f"Enter the name/category for expense {count}: ")
    expense_amount = int(input(f"Enter the amount for expense {count}: "))
    
    # Store as a tuple/dictionary in our list
    expenses_list.append({"name": expense_name, "amount": expense_amount})
    
    answer = input("Do you have any more expenses? (yes/no): ").lower()
    count += 1

# Calculate total
total = sum(item["amount"] for item in expenses_list)

# Print Table Header
print("\n" + "=" * 40)
print(f"{'EXPENSE NAME':<25} | {'AMOUNT':>10}")
print("=" * 40)

# Print each expense in tabular format
for item in expenses_list:
    print(f"{item['name']:<25} | ${item['amount']:>9,}")

print("-" * 40)
print(f"{'Total Expense':<25} | ${total:>9,}")
print(f"{'Monthly Budget':<25} | ${budget:>9,}")
print("=" * 40)

# Final summary
if budget - total >= 0:
    print(f"Status: You are UNDER budget by ${budget - total:,}")
else:
    print(f"Status: You are OVER budget by ${abs(budget - total):,}")
"""
print("="*50)
print(f"{'EXPENSE NAME':<25} | {'AMOUNT':>10}")
print("-"*50)
print("\n\n\n\n\n")
print("-"*50)
expenses_list = []
for item in expenses_list:
    print(f"{item['name']:<25} | ${item['amount']:>9,}")