# 1. Energy-Saving Automatic Outside Light  
*A Microcontroller-Based Smart Lighting System*

## Team
- Pietro Di Penta
- Sheng Jiang

## Project Aim
Design and program a fully automatic outside-light controller that:
- Detects ambient light using an LDR.
- Displays current hour in binary on the LED array.
- Forces lamp OFF between approximately 01:00 and 05:00.
- Applies UK daylight savings transitions automatically.
- Maintains long-term synchrony with the sun.
- Requires no routine maintenance after setup.
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

The firmware is interrupt-driven and uses a small set of modules:
- `timers.c` + `interrupts.c` provide minute ticks and light-transition events.
- `clock.c` + `dates.c` manage calendar logic, DST, leap years, and expected solar noon.
- `ADC.c` + `comparator.c` convert LDR readings into sunrise/sunset events.
- `LEDarray.c` + `LCD.c` provide output visualization.
- `main.c` orchestrates state updates, drift correction, output control, and sleep.

### Requirement Mapping
1. Day/night detection with LDR:
`ADC_init`, `ADC_getval`, `Comp1_init`, comparator interrupt events (`sunrise_event`, `sunset_event`).

2. Binary hour display:
`LEDarray_disp_bin(dt.time.hour)` in `main.c`.

3. Power-saving OFF window (1am-5am):
`LIGHT_OFF_HOUR_AM` and `LIGHT_ON_HOUR_AM` in `main.c` enforce lamp OFF during this range.

4. DST support:
UK DST boundaries are calculated with `last_sunday_of_month` and applied in `increase_clock_by_minute`.

5. Long-term solar synchrony:
Measured solar noon from sunrise/sunset is compared with modeled solar noon (`today_solar_noon_min`), then corrected using a moving average.

6. Fully automatic behavior:
After initial date/time constants are set, the runtime loop is autonomous.

## 6. How It Works

1. Initialize peripherals and startup state.
2. Consume ISR-produced minute ticks.
3. Capture sunrise/sunset edges from comparator ISR.
4. At end of each observed day, compute noon error and update drift estimate.
5. Refresh LCD and LED outputs.
6. Sleep in Idle mode until next interrupt.
---

## 7. Testing Mode and Key Configuration

- `config.h`
`testing_mode = 1` for accelerated testing, `0` for real-time operation.

- `main.c`
`LIGHT_OFF_HOUR_AM` and `LIGHT_ON_HOUR_AM` define the forced-off period.
`MAX_DRIFT_VAL` limits applied drift correction.

- `main.c`
`dt` contains initial date/time and is used to bootstrap weekday/DST state.
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
---

## 11. Notes

- Designed for UK daylight saving time rules  
- Solar synchronisation ensures indefinite long-term accuracy  
- The design can be adapted to other regions with minimal modification

---
## 12. Core Algorithms (Condensed)

This project uses a small set of efficient, deterministic algorithms designed for long-term accuracy on a resource-constrained microcontroller. All algorithms operate using integer arithmetic and interrupt-driven events.

---

### 12.1 Ambient Light Detection

Ambient light is measured using an LDR sampled via ADC/comparator hardware.  
A fixed threshold distinguishes day from night, with stable edge detection to avoid rapid toggling at dawn and dusk.

- Day → light forced OFF  
- Night → light allowed ON (subject to time rules)

---

### 12.2 Internal Real-Time Clock

Time is maintained entirely in software using a hardware timer interrupt.  
Each minute tick updates seconds, minutes, hours, and calendar date, including correct month lengths and leap years.

The clock runs continuously without an external RTC.

---

### 12.3 Binary Hour Display

The current hour (0–23) is displayed in binary on an LED array.  
Each bit of the hour value directly drives one LED, updating only when the hour changes.

---

### 12.4 Energy-Saving Time Window

To reduce unnecessary power usage, the lamp output is forced OFF between approximately 01:00 and 05:00, regardless of ambient light conditions.  
Outside this window, lamp behavior depends solely on day/night detection.

---

### 12.5 Daylight Saving Time (UK)

UK daylight saving rules are handled automatically in software:

- Clock moves forward on the last Sunday of March  
- Clock moves backward on the last Sunday of October  

Transition dates are computed dynamically each year, with leap years handled correctly.

---

### 12.6 Solar Synchronisation and Drift Correction

Sunrise and sunset events are inferred from LDR transitions.  
The midpoint between these events is used to estimate solar noon, which is compared to a modeled solar noon value.

A bounded moving-average correction is applied gradually to prevent long-term clock drift while avoiding instability from daily noise.

---

### 12.7 Accelerated Testing Mode

A compile-time testing mode scales timer intervals so that simulated time passes faster (e.g. one second represents one hour).  
All control logic remains identical between testing and real-time operation.


## Efficiency Highlights
The current code includes multiple efficiency-focused ideas:

- Interrupt handlers are minimal and flag-based (`interrupts.c`):
ISRs only queue work (`unprocessed_minutes`, sunrise/sunset flags) and avoid heavy processing.

- Priority-based ISR separation (`interrupts.c`):
Timer0 runs high priority and comparator runs low priority, preserving timing accuracy.

- Idle sleep between events (`main.c`):
`CPUDOZEbits.IDLEN = 1` plus `Sleep()` reduces active CPU time and power draw.

- Integer-only time and solar calculations (`clock.c`, `main.c`):
No floating-point math is used in runtime control loops.

- Precomputed equation-of-time lookup table (`clock.c`):
Daily solar-noon modeling uses a static table instead of expensive real-time trig/math.

- Circular history buffer for drift (`main.c`):
A fixed-size 7-sample window keeps RAM usage predictable and small.

- Moving-average drift correction (`main.c`):
Smoothing daily noise prevents overreaction to single-day outliers.

- Clamped correction magnitude (`MAX_DRIFT_VAL` in `main.c`):
Limits instantaneous correction steps for stable behavior.

- Fast-path minute step logic (`clock.c`):
`increase_clock_by_minute` exits quickly for non-rollover minutes.

- Compile-time test acceleration (`testing_mode` in `config.h`):
Allows rapid validation (about one simulated day per 24 seconds) without changing main logic.

- Hardware mapping centralization (`board_layout.h`):
Pin mapping macros reduce duplication, simplify maintenance, and lower wiring/configuration error risk.
