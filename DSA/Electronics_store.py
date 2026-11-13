import time

Laptop = int(input("Enter the number of laptops in stock : "))
Mouse = int (input("Enter the number of Mouse in stock : "))
Keyboard = int(input("Enter the number of keyboard in stock : "))

Laptop_price = 55000
Mouse_price = 800
Keyboard_price = 1500

start = time.perf_counter()
print("The total stack value of Laptop : ", Laptop*Laptop_price )
print("The total stock value of Mouse : ", Mouse*Mouse_price)
print("The total stock value fo Keyboard : ", Keyboard*Keyboard_price)
print("Total stock value = ",Laptop_price*Laptop + Mouse_price*Mouse + Keyboard_price*Keyboard)
end = time.perf_counter()
print("TIME TAKEN : ",(end - start)*1000," ms")
