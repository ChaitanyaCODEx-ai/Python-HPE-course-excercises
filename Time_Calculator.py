response = int(input("Enter the amount of seconds :"))

if response <= 60:
    print(f"{response} seconds")

elif 60 < response <= 3600:
    minutes = response//60
    seconds = response%60
    print(minutes,"min",seconds,"sec")

elif 3600 < response <= 86400:
    hours = response//3600
    sec = response%3600
    min = sec//60
    second = sec%60
    print(hours,"hrs",min,"min",second,"sec")
    
elif 86400 < response:
    days = response // 86400
    sec = response % 86400
    hours = sec // 3600
    sec = sec % 3600
    minutes = sec // 60
    seconds = sec % 60
    print(f"{days} days {hours} hrs {minutes} min {seconds} sec")