hot_dogs_per_package = 10
buns_per_package = 8

people = int(input("Number of people that will attend the cookout : "))
hot_dogs_per_person = int(input("Number of hot dogs required per person : "))

Hot_dog_package_required = (people*hot_dogs_per_package+9)//10
Bun_package_required = (people*buns_per_package+7)//8

print("Number of packages of hot dogs required : ", Hot_dog_package_required)
print("Number of packages of hot dog buns required : ", Bun_package_required)

Left_over_Hot_Dogs = (Hot_dog_package_required*10 - hot_dogs_per_person*people)
Left_over_buns = (Bun_package_required*8 - hot_dogs_per_person*people)

print("Number of hot dogs that will be left over : ", Left_over_Hot_Dogs)
print("Number of hot dog buns that will be left over : ", Left_over_buns)