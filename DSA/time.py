import time                                     # bring in the time library, gives us access to tools for tracking time and performance.
year = int(input("Enter a year: "))             # read the year 
start = time.perf_counter()                     # records the current time, provides a high-precision clock used as a stopwatch starting point right before the leap year calculations begin.
if year%400 == 0:
    result = "Leap year"
elif year%100 == 0:
    result = "not a leap year"
elif year % 4 == 0:
    result = "Leap year"
else:
    result = "Not a leap year"
end = time.perf_counter()
print(result)
print("Time taken : ",(end-start)*1000,"ms")

'''At a high level, this script does two main things: determines whether a user-entered year is a leap year and measures the exact execution time of that calculation.

Here is a breakdown of how the components work together:

1. User Input and Performance Timing Setup
Getting the Year: The program prompts you to type a year, reads your input, and converts it into an integer so it can perform mathematical operations on it.

Starting the Stopwatch: Before running the logic, it calls time.perf_counter(). This acts as a high-precision digital stopwatch to measure performance down to fractions of a millisecond.

2. The Leap Year Logic (Gregorian Calendar Rules)
The script uses standard calendar rules to check divisibility using the modulo operator (%), which finds the remainder of a division:

Centuries (Divisible by 400): If a year ends in 00, it must be divisible by 400 to be a leap year (e.g., 2000 is a leap year).

Centuries (Divisible by 100): If it's divisible by 100 but not 400, it is skipped and marked as not a leap year (e.g., 1900 is not a leap year).

Standard Years (Divisible by 4): Any other year divisible by 4 is a leap year (e.g., 2024).

Default: If it fails all these checks, it is not a leap year.

3. Output and Benchmarking
Result Display: It prints whether the year is a leap year or not.

Performance Calculation: It stops the stopwatch (end), subtracts the start time from the end time to get the duration in seconds, multiplies it by 1,000 to convert it into milliseconds, and prints how fast the computer processed your request.'''