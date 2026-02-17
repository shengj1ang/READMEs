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
 
![P1](https://raw.githubusercontent.com/shengj1ang/READMEs/refs/heads/ECM-labx/images/P1.png)

![P2](https://raw.githubusercontent.com/shengj1ang/READMEs/refs/heads/ECM-labx/images/P2.png)

![P3](https://raw.githubusercontent.com/shengj1ang/READMEs/refs/heads/ECM-labx/images/P3.png)

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

No — the LED still stays off.


- What is the value of the variable when the if comparison is done? (Use debug mode)

![P4](https://raw.githubusercontent.com/shengj1ang/READMEs/refs/heads/ECM-labx/images/P4.png)

In debug mode on the PIC, value = 0.100000024 while expected (float)ZZ = 0.1 (stored float). Since they are not exactly equal, value == ZZ is false.

(Watch window showing 0.0 is almost certainly a display/format precision issue — increase the displayed precision / view the raw hex to see the non-zero value.)



- Also compare the size of the program again, is it what you expected?

![P5](https://raw.githubusercontent.com/shengj1ang/READMEs/refs/heads/ECM-labx/images/P5.png)

	•	Program Used: 1,532 bytes

	•	Data Used: 20 bytes

This is still much larger than the original integer-only version (72 bytes program, 2 bytes data), but smaller than the earlier mixed float/int build, because now the compiler can use float routines consistently.

Try the same calculation in Excel and/or Python and/or MATLAB. Note you will need to ensure that enough significant figures are displayed to see what is happening (at least 16 decimal places)

- Do you get the expected result?

	•	Python float is IEEE-754 double (64-bit), so:

	•	1.2 is stored as 1.19999999999999996

	•	1.1 is stored as 1.10000000000000009

	•	0.1 is stored as 0.10000000000000001

	•	therefore 1.2 - 1.1 = 0.09999999999999987, not exactly 0.1

	•	So (a-b) == z is False, but diff is tiny (~1.39e-16), and math.isclose is True.

- Was it the same value as on the PIC?

No. Python uses 64-bit double so the error is around 10^{-16}, while the PIC uses 32-bit float so the rounding error is much larger (around 10^{-8}). Therefore get a different stored value and a different subtraction result.

- What is going on? Why are you seeing these values?

Numbers like 0.1, 1.1 and 1.2 cannot be represented exactly in binary floating-point, so they are stored as the nearest representable values. The subtraction is then performed on these approximations and rounded again, so the result is close to 0.1 but not exactly equal. This is why == fails and why a tolerance check (e.g., isclose / epsilon) is needed.

# Precision
This is not just an issue when floats are used to store decimal point numbers, similar issues can occur when floats are used to store integer numbers. Try changing the values as follows (keeping the float type)

    #define XX 920020001
    #define YY 1
    #define ZZ 920020000
    
- Does the LED light up as expected?

LED does not light up 

- What is the value of the variable when the if comparison is done? (Use debug mode)

![P7](https://raw.githubusercontent.com/shengj1ang/READMEs/refs/heads/ECM-labx/images/P7.png)

In debug, value ≈ 9.2002003E8 while expected (float)ZZ ≈ 9.2001997E8; the difference is diff = 64.0.

Why?

At around 9.2\times10^8, a 32-bit float cannot represent every integer. The spacing between adjacent representable floats is 64, so XX, ZZ, and XX-1 round to different multiples of 64 and the equality test fails.

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
