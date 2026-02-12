# 1. Energy-Saving Automatic Outside Light  
*A Microcontroller-Based Smart Lighting System*

---

## 2. Project Overview

This project implements a fully automated, energy-efficient outside lighting system using a microcontroller, inspired by real-world street and garden lighting solutions.  
The system intelligently reacts to ambient light levels, keeps accurate time, adjusts for daylight saving time (DST), and minimizes unnecessary energy consumption by switching lights off during low-activity hours.

Once installed, the system requires zero user maintenance and remains synchronized with natural daylight indefinitely.

---

## 3. Key Features

1. **Ambient Light Detection**  
   Uses an LDR (Light Dependent Resistor) to detect day and night conditions and control lighting automatically.

2. **Real-Time Clock System**  
   Maintains time internally and displays the current hour in binary on an LED array, as well as user-friendly time and DST status on an LCD screen.

3. **Smart Energy Saving Mode**  
   Automatically turns the light off between approximately 01:00 and 05:00, even if it is dark.

4. **Daylight Saving Time Support (UK)**  
   Automatically adjusts clocks:
   - Forward on the last Sunday in March  
   - Backward on the last Sunday in October  
   - Leap years are handled correctly

5. **Solar Synchronisation**  
   Uses sunrise and sunset detection to prevent long-term clock drift and remain aligned with the sun.

6. **Fully Automatic Operation**  
   No recalibration or manual input is required after installation.

---

## 4. System Design

The project follows a modular design, with each hardware and software responsibility isolated into its own source file.  
This improves readability, maintainability, and ease of testing.

---

## 5. Project Structure
├── main.c          # Program entry point and system orchestration
├── clock.c         # Timekeeping and hour/minute/second management
├── dates.c         # Date handling, leap years, and DST calculations
├── timers.c        # Hardware timer configuration and timing logic
├── interrupts.c   # Interrupt service routines (ISR)
├── comparator.c   # LDR signal comparison and threshold detection
├── LEDarray.c     # Binary hour display on LED array
├── LCD.c          # LCD output for time and status display
---

## 6. How It Works

1. **Startup**
   - Hardware timers and interrupts are initialized  
   - Internal clock and date tracking begin

2. **Light Monitoring**
   - The LDR is continuously sampled  
   - Ambient brightness determines day or night state

3. **Lighting Control**
   - At night: LED turns ON  
   - Between 01:00 and 05:00: LED is forced OFF  
   - During daylight: LED remains OFF

4. **Time Display**
   - Current hour is displayed in binary on the LED array  
   - Readable time and DST status are shown on the LCD

5. **Long-Term Accuracy**
   - Sunrise and sunset timing is used to correct clock drift  
   - Day length information helps infer season and DST transitions

---

## 7. Testing Mode

To speed up development and debugging, the system supports a testing mode:

- A full 24-hour day can be simulated in 24 seconds  
- Controlled via a compile-time `#define` directive  
- Enables rapid validation of:
  - Day and night transitions  
  - Daylight saving time changes  
  - Energy-saving time window logic

---

## 8. Hardware Requirements

- Microcontroller (as used in Labs 1–3)
- Light Dependent Resistor (LDR)
- LED (outside light simulation)
- LED array (binary hour display)
- Optional LCD display
- Supporting resistors and wiring

---

## 9. Learning Outcomes

Through this project, the following skills are developed:

- Designing a real-world embedded system  
- Writing modular and maintainable C code  
- Working with timers, interrupts, and hardware peripherals  
- Implementing time, date, and daylight saving logic  
- Handling long-term system accuracy and clock drift

---

## 10. Getting Started

1. Clone this repository:
  
```
git clone <repository-url>
   	2.	Open the project in your microcontroller IDE
	3.	Compile and flash to the target hardware
	4.	(Optional) Enable testing mode for rapid simulation
```
  📝 Notes
•	Designed for UK daylight saving rules
•	Solar synchronization ensures indefinite accuracy
•	Suitable for adaptation to other regions with minimal changes
---

## 11. Notes

- Designed for UK daylight saving time rules  
- Solar synchronisation ensures indefinite long-term accuracy  
- The design can be adapted to other regions with minimal modification

---

## 12. Core Algorithms

This project relies on a set of robust, lightweight algorithms designed to run efficiently on a microcontroller while remaining accurate over long periods of time.

---

### 12.1 Ambient Light Detection Algorithm

**Purpose:**  
Determine whether it is currently day or night using an LDR.

**Method:**  
- The LDR output is sampled periodically using a comparator or ADC  
- A predefined threshold distinguishes bright (day) from dark (night) conditions  
- Stable sampling avoids rapid switching at dawn and dusk

**Result:**  
- Night detected: light is allowed to turn ON (subject to time rules)  
- Day detected: light is forced OFF

---

### 12.2 Real-Time Clock (RTC) Algorithm

**Purpose:**  
Maintain accurate time without an external RTC module.

**Method:**  
- A hardware timer generates periodic interrupts  
- On each interrupt:
- Seconds are incremented  
- Overflow propagates to minutes, hours, and days  
- Date tracking includes leap year and month length handling

**Result:**  
- A continuously running internal clock  
- Current time always available for display and control

---

### 12.3 Binary Hour Display Algorithm

**Purpose:**  
Display the current hour of the day in binary on an LED array.

**Method:**  
- The hour value (0–23) is masked bit-by-bit  
- Each bit controls a corresponding LED  
- LEDs update whenever the hour changes

**Example:**  
Hour = 13 → Binary = 01101
**Result:**  
- Simple and hardware-efficient time visualization

---

### 12.4 Energy-Saving Time Window Algorithm

**Purpose:**  
Reduce unnecessary lighting during low-activity hours.

**Method:**  
- The current hour is checked during each control cycle  
- Between 01:00 and 05:00:
  - Light output is forced OFF regardless of ambient light  
- Outside this window:
  - Light behavior depends on LDR input

**Result:**  
- Reduced energy consumption  
- Predictable and policy-driven behavior

---

### 12.5 Daylight Saving Time Adjustment Algorithm

**Purpose:**  
Automatically adjust the system clock according to UK DST rules.

**Method:**  
- Tracks the current date and day of the week  
- DST transitions occur on:
  - Last Sunday of March (clock moves forward one hour)  
  - Last Sunday of October (clock moves backward one hour)  
- Leap years are handled correctly

**Result:**  
- Fully automatic DST handling  
- No user intervention required

---

### 12.6 Solar Synchronisation Algorithm

**Purpose:**  
Prevent long-term clock drift and maintain alignment with solar time.

**Method:**  
- Sunrise and sunset are inferred from LDR transitions  
- The midpoint between dusk and dawn approximates solar midnight or noon  
- Small corrective adjustments are applied when drift is detected  
- Seasonal day length variation provides time-of-year context

**Result:**  
- Indefinite long-term accuracy  
- Synchronisation with the sun rather than a perfect oscillator

---

### 12.7 Testing Acceleration Algorithm

**Purpose:**  
Enable rapid testing without waiting for real-time day cycles.

**Method:**  
- A compile-time `#define` scales timer intervals  
- In testing mode:
  - One second represents one hour  
- All control logic remains unchanged

**Result:**  
- Fast debugging and validation  
- Identical logic in testing and deployment builds