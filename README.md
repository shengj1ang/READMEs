# When computers can't add up
Computers are designed to store, manipulate and perform calculations with numbers. For the most part, they are extremely good at this, much better than us humans. However, there are limitations and instances where the results produced may not be as expected and as a programmer you should be aware of these. This lab is compulsory for 4th year students and optional 3rd year students. 

## Learning outcomes

The principal learning objectives for this lab are:

- Appreciate the issues and limitations of how computers store numbers
- Recognise and troubleshoot errors in calculations

## Lab submission
Please edit this readme to record your answers to the questions throughout the lab. Answers should be as concise as possible, a small list of bullet points is acceptable. We are not expecting essays here.

# Integers
```
#define XX 12
#define YY 11
#define ZZ 1
```
Run the example main.c file given in this repo and check that it behaves as expected when running on your Clicker board. The code performs a simple integer calculation and compares the result to the expected value. In the initial case the calculation should work fine and an LED (RD7) will light up.


Now edit the numbers in the calculation by changing the values to be a 10th of the original value, as shown below.
```
#define XX 1.2
#define YY 1.1
#define ZZ 0.1
 ```
Image1
Image2
Image3

1) What result do you get?
The LED stays off.

2) What is the value of the variable when the if comparison is done?
value is 0 (0x0000) at the comparison.

3) Was this expected and why?
Yes. value is an int, but XX, YY, and ZZ are floating-point constants. Assigning a float to an int truncates the fractional part, so 1.2 becomes 1 and 1 - 1.1 becomes 0 after truncation, making the comparison with 0.1 fail.

4) What is the size of the program and data memory used in bytes? How does this compare to the original code?
Original: Program Used 72 bytes, Data Used 2 bytes.
Modified: Program Used 2,278 bytes, Data Used 42 bytes.
The modified version uses much more program (and slightly more data) memory due to floating-point support code.
# Floats to the rescue?
The integer example above may have gone wrong for obvious reasons. We might expect that changing the variable to be a floating point number would produce the correct result. Try this and see what happens when you run the program.

    volatile float value;
  
- Did you get the expected result?
- What is the value of the variable when the if comparison is done? (Use debug mode)
- Also compare the size of the program again, is it what you expected?

Try the same calculation in Excel and/or Python and/or MATLAB. Note you will need to ensure that enough significant figures are displayed to see what is happening (at least 16 decimal places)

- Do you get the expected result?
- Was it the same value as on the PIC?
- What is going on? Why are you seeing these values?

# Precision
This is not just an issue when floats are used to store decimal point numbers, similar issues can occur when floats are used to store integer numbers. Try changing the values as follows (keeping the float type)

    #define XX 920020001
    #define YY 1
    #define ZZ 920020000
    
- Does the LED light up as expected?
- What is the value of the variable when the if comparison is done? (Use debug mode)

Try changing the value of XX to the below and seeing what happens

    #define XX 920020000
    
- Why Does the LED light up despite the calculation being wrong?
- How does the precision of floating point numbers change with magnitude?

Finally, change XX back to the previous value (920020001) and change the type to long int as below:

    volatile long int value;

- Is everything working as expected?
- Check the size of the program and data memory used in bytes and compare to the previous.

The examples above show that no number system is perfect and they each have their own issues and limitations. It is important to be mindful of how computers store numbers and perform calculations. On 8-bit microcontrollers (or any microcontroller without a hardware floating-point unit) it is much more efficient to use integer types and occasions that truly justify using floats are extremely rare. 

# Further reading
https://www.h-schmidt.net/FloatConverter/IEEE754.html

https://docs.python.org/3/tutorial/floatingpoint.html

https://www.lahey.com/float.htm

https://www3.ntu.edu.sg/home/ehchua/programming/java/datarepresentation.html (an in depth description of all types IEEE chap. 4 for 32-bit floats)
