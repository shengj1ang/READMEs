# 🌙 Energy-Saving Automatic Outside Light  
*A Microcontroller-Based Smart Lighting System*

---

## 📌 Project Overview

This project implements a **fully automated, energy-efficient outside lighting system** using a microcontroller, inspired by real-world street and garden lighting solutions.  
The system intelligently reacts to ambient light levels, keeps accurate time, adjusts for daylight saving time (DST), and minimizes unnecessary energy consumption by switching lights off during low-activity hours.

Once installed, the system requires **zero user maintenance** and remains synchronized with natural daylight indefinitely.

---

## 🎯 Key Features

- 🌗 **Ambient Light Detection**  
  Uses an LDR (Light Dependent Resistor) to detect day/night conditions and control lighting automatically.

- ⏰ **Real-Time Clock System**  
  Maintains time internally and displays the **current hour in binary** on an LED array and on LCD screen.

- 💡 **Smart Energy Saving Mode**  
  Automatically turns the light **off between ~1:00 AM and 5:00 AM**, even if it is dark.

- 🌍 **Daylight Saving Time Support (UK)**  
  Automatically adjusts clocks:
  - Forward on the **last Sunday in March**
  - Backward on the **last Sunday in October**
  - Leap years are handled correctly

- ☀️ **Solar Synchronisation**  
  Uses sunrise and sunset detection to prevent long-term clock drift and stay aligned with the sun.

- 🔧 **Fully Automatic Operation**  
  No recalibration or manual input required after installation.

---

## 🧠 System Design

The project is modular, with each hardware and software responsibility isolated into its own source file.  
This improves readability, maintainability, and testing.

---

## 📂 Project Structure
├── main.c          # Program entry point and system orchestration
├── clock.c         # Timekeeping and hour/minute/second management
├── dates.c         # Date handling, leap years, DST calculations
├── timers.c        # Hardware timer configuration and timing logic
├── interrupts.c   # Interrupt service routines (ISR)
├── comparator.c   # LDR signal comparison and threshold detection
├── LEDarray.c     # Binary hour display on LED array
├── LCD.c          # Optional LCD output (status/debugging)

---

## ⚙️ How It Works

1. **Startup**
   - Timers and interrupts are initialized
   - Internal clock and date tracking begin

2. **Light Monitoring**
   - The LDR is continuously sampled
   - Ambient brightness determines day or night state

3. **Lighting Control**
   - At night: LED turns **ON**
   - Between **01:00–05:00**: LED is forced **OFF**
   - During daylight: LED remains **OFF**

4. **Time Display**
   - Current hour is displayed in **binary** on the LED array, user friendly time and DST status on the LCD.

5. **Long-Term Accuracy**
   - Sunrise/sunset timing is used to correct clock drift
   - Day length helps infer season and DST transitions

---

## 🧪 Testing Mode

To speed up development and debugging, the system supports a **testing mode**:

- A full 24-hour day can be simulated in **24 seconds**
- Controlled via a `#define` directive
- Enables rapid validation of:
  - Night/day transitions
  - DST changes
  - Energy-saving window logic

---

## 🛠️ Hardware Requirements

- Microcontroller (as used in Labs 1–3)
- Light Dependent Resistor (LDR)
- LED (outside light simulation)
- LED array (binary hour display)
- Optional LCD display
- Supporting resistors and wiring

---

## 📚 Learning Outcomes

Through this project, the following skills are developed:

- Designing a **real-world embedded system**
- Writing **modular and maintainable C code**
- Working with **timers, interrupts, and hardware peripherals**
- Implementing **time, date, and DST logic**
- Handling **long-term system accuracy and drift**

---

## 🚀 Getting Started

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

## 🧠 Core Algorithms

This project relies on a small set of robust, lightweight algorithms designed to run efficiently on a microcontroller while remaining accurate over long periods of time.

---

### 1️⃣ Ambient Light Detection Algorithm

**Purpose:**  
Determine whether it is currently day or night using an LDR.

**Method:**
- The LDR output is sampled periodically via a comparator/ADC.
- A predefined threshold distinguishes *bright* (day) from *dark* (night).
- To avoid rapid toggling at dusk and dawn, the algorithm implicitly relies on stable sampling over time.

**Result:**  
- **Night detected →** Light allowed to turn ON (subject to time rules)  
- **Day detected →** Light forced OFF

---

### 2️⃣ Real-Time Clock (RTC) Algorithm

**Purpose:**  
Maintain accurate time (seconds, minutes, hours, days) without an external RTC module.

**Method:**
- A hardware timer generates periodic interrupts (e.g. every second).
- On each interrupt:
  - Seconds increment
  - Overflow propagates to minutes, hours, and days
- Date information is updated continuously, including:
  - Day of week
  - Month length
  - Leap year handling

**Result:**  
- A continuously running internal clock with minimal overhead
- Current hour is always available for display and control logic

---

### 3️⃣ Binary Hour Display Algorithm

**Purpose:**  
Display the current hour of the day on an LED array in binary format.

**Method:**
- The hour value (0–23) is masked bit-by-bit.
- Each bit maps directly to one LED in the array.
- LEDs are updated whenever the hour changes.

**Example:**  
Hour = 13  →  Binary = 01101

**Result:**  
- Clear, hardware-efficient visual representation of time
- No need for complex display drivers

---

### 4️⃣ Energy-Saving Time Window Algorithm

**Purpose:**  
Prevent unnecessary lighting during low-activity hours.

**Method:**
- Each control cycle checks the current hour.
- If the time lies between approximately **01:00 and 05:00**:
  - The light output is forced OFF, regardless of ambient light.
- Outside this window:
  - Light behavior depends on LDR input.

**Result:**  
- Significant energy savings
- Predictable and policy-driven lighting behavior

---

### 5️⃣ Daylight Saving Time (DST) Adjustment Algorithm

**Purpose:**  
Automatically adjust the system clock according to UK DST rules.

**Method:**
- The algorithm tracks:
  - Current date
  - Day of week
- DST transitions occur when:
  - **Last Sunday of March → clock +1 hour**
  - **Last Sunday of October → clock −1 hour**
- Leap years are handled to ensure correct calendar alignment.

**Result:**  
- Fully automatic DST handling
- No user input or reprogramming required

---

### 6️⃣ Solar Synchronisation Algorithm

**Purpose:**  
Prevent long-term clock drift and maintain alignment with real solar time.

**Method:**
- Sunrise and sunset times are inferred from LDR transitions.
- The midpoint between dusk and dawn approximates **solar midnight/noon**.
- Small corrective adjustments are applied to the internal clock when drift is detected.
- Seasonal day-length variation is also used to infer time-of-year context.

**Result:**  
- Indefinite long-term accuracy
- Clock remains synchronized with the sun rather than relying on a perfect oscillator

---

### 7️⃣ Testing Acceleration Algorithm (Development Mode)

**Purpose:**  
Enable fast testing without waiting for real 24-hour cycles.

**Method:**
- A compile-time `#define` scales timer intervals.
- In testing mode:
  - **1 second ≈ 1 hour**
- All other algorithms remain unchanged.

**Result:**  
- Rapid debugging and validation
- Identical logic in both test and real deployments

