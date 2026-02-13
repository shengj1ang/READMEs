# Energy Saving Automatic Outside Light - Documentation

## Team
- Pietro Di Penta
- Sheng

## Project Aim
Design and program a fully automatic outside-light controller that:
- Detects ambient light using an LDR.
- Displays current hour in binary on the LED array.
- Forces lamp OFF between approximately 01:00 and 05:00.
- Applies UK daylight savings transitions automatically.
- Maintains long-term synchrony with the sun.
- Requires no routine maintenance after setup.

## System Overview
The firmware is interrupt-driven and uses a small set of modules:
- `timers.c` + `interrupts.c` provide minute ticks and light-transition events.
- `clock.c` + `dates.c` manage calendar logic, DST, leap years, and expected solar noon.
- `ADC.c` + `comparator.c` convert LDR readings into sunrise/sunset events.
- `LEDarray.c` + `LCD.c` provide output visualization.
- `main.c` orchestrates state updates, drift correction, output control, and sleep.

## Requirement Mapping
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

## Runtime Flow
1. Initialize peripherals and startup state.
2. Consume ISR-produced minute ticks.
3. Capture sunrise/sunset edges from comparator ISR.
4. At end of each observed day, compute noon error and update drift estimate.
5. Refresh LCD and LED outputs.
6. Sleep in Idle mode until next interrupt.

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

## Key Configuration
- `config.h`
`testing_mode = 1` for accelerated testing, `0` for real-time operation.

- `main.c`
`LIGHT_OFF_HOUR_AM` and `LIGHT_ON_HOUR_AM` define the forced-off period.
`MAX_DRIFT_VAL` limits applied drift correction.

- `main.c`
`dt` contains initial date/time and is used to bootstrap weekday/DST state.

## References
External references used in project documentation/comments and related implementation:

1. Tomohiko Sakamoto weekday algorithm (`dates.c` comment):
https://www.geeksforgeeks.org/dsa/tomohiko-sakamotos-algorithm-finding-day-week/

2. Solar-noon equation source (`clock.c` comment):
http://www.egr.unlv.edu/~eebag/Properties%20of%20Sunlight%20-%20Part%20II.pdf


