#eACH DICTIONARY REPRESENTS ONE COMPLETE PRODUCT RECORD
products = [
    {"name": "Laptop", "price": 55000, "stock" : 12},
    {"name" : "mouse", "price" : 800, "stock" : 50},
    {"name" : "Keyboard", "price" : 1500, "stock" : 25},
]
total_value = 0
for product in products:
    unit_price = product["price"]
    quantity = product["stock"]
    total_value += unit_price * quantity
print("Total inventory value: ", total_value)

#Add a new product without changing the loop
products.append({"name": "Monitor", "price": 12000, "stock": 8})
print("Products now: ", len(products))