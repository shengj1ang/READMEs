# ECM buggy manual

## Introduction

This project develops an autonomous mobile robot designed for “mine navigation search and rescue”-style courses, where movement decisions are encoded by coloured cards placed along the maze walls. The robot must repeatedly locate a card, approach it without collision, identify its colour, and translate that colour into a navigation instruction (e.g., turn 90°, turn 135°, reverse then turn). After reaching the final Finish card (white), the robot must autonomously return to its starting position. If the finish cannot be located or the robot becomes uncertain about what it is seeing, it should enter a safe recovery behaviour and still attempt to return home.

The environment is a constrained maze built from black plywood walls with coloured cards attached at decision points. The colour set includes multiple hues that can be close under real lighting (for example blue vs light blue), so the system must be robust to brightness changes, sensor noise, and varying card distance. Because the robot’s navigation is entirely driven by card readings (the course layout and sequence are unknown in advance), reliable colour recognition and repeatable vehicle control are the two most important technical components of the solution.

## System Architecture
### 2.1 Hardware overview (chassis, motors/driver, colour sensor, MCU)

### 2.2 Software overview (modules, data flow)

## Motion Control

### Bi-directional linear motion control

The linear movement of the buggy is controlled in increments equal to one third of the maze wall length, which corresponds approximately to the length of the buggy. This discrete step size allows the robot to align with the grid-based structure of the maze, enabling more accurate path tracking and consistent positioning at each junction. As a result, movement control becomes simpler and navigation decisions can be executed more reliably.

**Advantages for returning home:**

Using incremental motion also simplifies the return-home functionality. Instead of storing the exact time or distance travelled, which would require greater memory and processing, the buggy records each movement increment and turn instruction in a stack data structure. Once the finish card is reached, the stack can be inverted to retrace the path in reverse order, enabling efficient real-time navigation while minimising memory usage and computational overhead.

The buggy moves with continuous linear motion, but its position is tracked using discrete increments, where one unit corresponds to one third of the maze wall length. To achieve this, the distance travelled in one unit step is calibrated using a trapezoidal power profile: the motors ramp up from rest, run at constant power, and then ramp down to rest. The area under this power–time profile corresponds to the distance travelled for one unit increment. When multiple increments are required, the same trapezoidal profile is used with a single ramp-up and ramp-down phase, while the duration of the constant-power segment is extended so that the total area under the curve matches the desired multiple of the unit distance.

Code Breakdown:

```
void executeAction(motion_controller *controller_state, const ActionStep *action_step)
{
    DC_motor *mL = &(controller_state->mL);
    DC_motor *mR = &(controller_state->mR);
    const unsigned char step_size = action_step->step_size;
    unsigned int duration_ms;
    switch (action_step->action) {
        ...
        case ACTION_FORWARD:
            fullSpeedAhead(mL, mR, FWD_LEFT_POWER, FWD_RIGHT_POWER);
            duration_ms = controller_state->delays.FORWARD_BASE_UNIT_MS * step_size;
            break;
    }
    delayMs(duration_ms);
    stop(mL, mR);
}
```

### Turning

Similar to linear motion, we adopt an incremental approach for turning. The smallest unit turn required in the maze is 45°, so we adopt and calibrate a trapezium-shaped wave to correspond to a left/right turn of 45°. For 90°, 135° or 180° turns, we simply repeat the 45° turn the required number of times. Whilst turns > 45° are not completely smooth, this approach requires no more than 4 pulsations, simplifying the calibration process, and minimising errors which are distributed across larger turns. Since the low-cost buggy's left and right motors are unlikely to behave identically, we calibrate and use seperate left and right 45° turns.

TODO) Update to reflect the fact that we don't actually do n 45 degree pulses , but one continous turn. Need to update the code though.

#### Code extract

```c
void executeAction(motion_controller *controller_state, const ActionStep *action_step)
{
    DC_motor *mL = &(controller_state->mL);
    DC_motor *mR = &(controller_state->mR);
    const unsigned char step_size = action_step->step_size;
    unsigned int duration_ms;
    switch (action_step->action) {
        ...
        case ACTION_TURN_LEFT:
            turnLeft(mL, mR, TURN_LEFT_POWER, TURN_RIGHT_POWER);
            duration_ms = controller_state->delays.TURN_LEFT_BASE_UNIT_MS * step_size;
            break;
    }
    delayMs(duration_ms);
    stop(mL, mR);
}
```

## Forward Mine Exploration Strategy

Whilst exploring the maze the buggy detects the colour cards and follows there instructions. To achieve an effective and efficient operation, the following logic was implemented:

1. Incremental Forward Motion
2. Wall Detection
3. Color Detection and Alignment
4. Follow Colour card Navigation Instruction
5. Record completed movement operations

This can also be seen in the following Figure:

##### Incremental Forward Motion

Forward motion is performed through a continuos motion, but the position is tracked incrementally through the following implementation:

##### Wall Detection

At the end of each incremental step in position the clear channel from the Color Click board is used to detect the wall of the maze, by comparing the clear channel value against a threshold:

##### Color Detection and Alignment

Once the buggy detects the wall it drives forward (to align) and implements the colour detection logic to capture RGB readings and record the colour of the card:

##### Follow Colour card Navigation Instruction

* **Red:** Reverse 1 step, turn 90 deg right, move forward
* **Green:** Reverse 1 step, turn 90 deg left, move forward
* **Blue:** Reverse 1 step, turn 180 deg, reverse to re-align, move forward
* **Yellow:** Reverse 1 square (3 steps), turn 90 deg right, move forward
* **Pink:** Reverse 1 square (3 steps), turn 90 deg left, move forward
* **Orange:** Reverse 1 step, turn 135 deg right, move forward
* **Light Blue:** Reverse 1 step, turn 135 deg left, move forward
* **White:** Flash LEDs to indicate end of Maze, return home
* **Black:** Flash LEDs to indicate got lost, return home

##### Record completed movement operations

Once a linear movment or turn is completed it is recorded on the instruction stack:

### Return Home Logic

The Return Home Logic allows the buggy to accurately retrace its route through the maze and return to the starting position after the finish card is detected. Instead of storing a full map of the maze, the system records the sequence of movement instructions executed during exploration and uses these to reconstruct the path in reverse.

##### Path Recording

During forward navigation, each movement command performed by the buggy (such as moving forward or executing a turn) is stored in an  instruction stack . This stack maintains the order of all actions taken while exploring the maze.

##### Path Reversal

Once the finish card is detected, the buggy reverses 1 step, performs a 180° rotation and reverses to re-align. This ensures the buggy faces back along the path it previously travelled. The stored instructions are then retrieved from the stack in reverse order.

##### Inverse Actions

For each instruction removed from the stack, the buggy performs the corresponding inverse movement:

* A **left turn** is reversed with a  **right turn** .
* A **right turn** is reversed with a  **left turn** .
* **Forward motion** can be executed again, without inversion, after the 180° rotation to move along the same path in the opposite direction.

#### Execution

By sequentially applying the inverse of each stored instruction, the buggy systematically retraces its route until the stack is empty, at which point it has returned to its original starting position. This approach provides a reliable and memory-efficient solution for returning home.

##### Advantages of the Return Home Logic

* **Low memory usage** – Only movement instructions are stored in a stack rather than full position coordinates or a map of the maze.
* **Computational efficiency** – Returning home simply requires reversing the instruction order and executing inverse actions, avoiding complex path-planning algorithms.
* **Scalability** – The method works for both simple and complex mazes since the number of stored instructions only grows with the number of movements made.
* **Accurate path retracing** – By undoing the exact sequence of actions taken during exploration, the buggy follows the same route back with high positional consistency.
* **Implementation simplicity** – The logic is straightforward to implement using basic data structures and motor control commands, improving system reliability and ease of debugging.

##### Navigation Logic Overview:

##### Video Demonstration:

##### Motion Calibration Procedure:

The motion calibration process ensures the buggy moves accurately and consistently within the maze. Because movement is controlled using **time-based motor commands** rather than wheel encoders, each step (such as moving one-third of a maze wall length) depends on the delay applied to the motors. Calibration therefore adjusts these delay values so that forward motion, reversing, and turning are reliable and repeatable. This is essential because both the navigation and return-home logic rely on these base movements being consistent.

### Purpose of Calibration

The aim of calibration is to adjust the delay values associated with each motion so that the buggy behaves as closely as possible to the intended maze movements. These values are tuned for the testing environment, by accounting for different track surfaces.

The calibration process improves the buggy’s ability to:

* Turn with precise increments of 45 deg both left and right
* move forward by  **one-third of a maze unit** ,
* move forward by  **one full maze unit** ,
* reverse by  **one-third of a maze unit** .

By calibrating these actions, the buggy is better able to align with the maze grid, respond correctly to colour instructions and retrace its path when required.

### Calibration Implementation

Calibration is run through a dedicated test mode in the main program. When the motor calibration mode is selected, the `calib()` function is called. This initialises the serial output, configures the two push buttons on **RF2** and  **RF3** , and sets up the **RH3** and **RD7** LEDs for visual feedback. The program then waits for the user to press **RF2** before starting the calibration sequence.

The actual motion of the buggy is carried out through the `executeAction()` function. This function applies the correct motor command for the chosen action, waits for a delay based on the stored calibration value, and then stops the motors. In this way, calibration directly updates the same delay values that are later used during normal maze navigation.

### Key Calibration Modes

The calibration routine is divided into five modes, each corresponding to a specific motion:

**Mode 1 – Left Turn Calibration**

This mode calibrates a 90° left turn. The buggy performs a left turn using two turning units (of 45 deg each), allowing the delay for left rotation to be adjusted until the turn is accurate.

**Mode 2 – Right Turn Calibration**

This mode calibrates a 90° right turn. The buggy performs a right turn using two turning units (of 45 deg each), allowing the delay for rightrotation to be adjusted until the turn is accurate.

**Mode 3 – Forward Motion Calibration (1/3 Unit)**

This mode calibrates the short forward movement used as the basic movement step. The buggy moves forward by one-third of a maze unit and the delay is adjusted until the distance is accurate.

**Mode 4 – Forward Motion Calibration (1 Full Unit)**

This mode calibrates a full forward maze unit. This ensures that longer straight movements also remain accurate and that the buggy can align properly with the maze layout.

**Mode 5 – Reverse Motion Calibration (1/3 Unit)**

This mode calibrates the reverse movement used for repositioning and backtracking. The buggy reverses by one-third of a maze unit and the corresponding delay is tuned.

#### Calibration Flow Chart

#### Calibration Execution

Each mode uses the same `calibration_execution()` function. This function first performs the selected motion, then allows the user to modify the associated delay value. The motion is repeated using the updated value until the user is satisfied with the result. This modular approach keeps the code structured and allows the same logic to be reused for all movement types.

#### User Calibration Interaction with Buggy

**Button Controls:**

* **RF2** increases the current delay value
* **RF3** decreases the current delay value
* **RF2 + RF3 together** confirm the delay and move to the next stage of the process

After adjusting the delay, the user is given the option either to **repeat the calibration move** using the new value (pressing RF2) or to **complete calibration of that mode and continue** to the next one (pressing RF3).

**LED Visual Feedback:**

* **RH3** flashes when a delay value is adjusted
* **RD7** flashes when a mode is confirmed or calibration begins

This provides immediate visual feedback to show that the button press has been detected and the input has been accepted, usefull when calibration is completed whilst car is not connected via serial comunication.



# Colour Recognition

## Data collection
We collect raw colour measurements from an RGB+C (Clear) sensor, which outputs four channels per sample: Red (R), Green (G), Blue (B), and Clear (C). The Clear channel represents overall brightness (total light intensity) and is useful for normalisation later.

Data is streamed from the microcontroller over UART as CSV lines with the fields:
mode, card_label, distance_mm, clear, red, green, blue.
On the PC side, a Python logger opens the serial port, sends a single start request in mode “A” (all LEDs on) together with the chosen card_label (distance is included only to satisfy the MCU request format), then continuously reads incoming samples and stores them in an SQLite database table (colordata) with a PC timestamp (time.time()).

## Data Analysis

After logging raw RGBC samples to SQLite, the next step was to check whether the colours are separable in a brightness-invariant space. Absolute RGB values change with distance and illumination, while **channel ratios** are more stable. Therefore, we analyse the dataset in the **normalised chromaticity space**:

\[
$r = \frac{R}{C},\quad g = \frac{G}{C},\quad b = \frac{B}{C}$
\]

First, we visualised all samples as a 3D scatter plot in \((r,g,b)\) to inspect overlap and outliers 
![3D-Normalized-RGB_Scatter](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/images_for_doc/3D-Normalized-RGB_Scatter.png?raw=true)

Most colours form compact clusters, but the closest clusters (e.g., *blue vs light blue*, *black vs green*) show partial overlap.

To summarise each cluster, we computed the **per-class mean** and **standard deviation** in \((r,g,b)\), and visualised each label as a mean point with a spread envelope (±3σ ellipsoid). This makes cluster separation and overlap easier to interpret 
![3D-Mean-with-SpreadEnvelopes.png](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/images_for_doc/3D-Mean-with-SpreadEnvelopes.png?raw=true)

These mean/std values later informed a statistical confidence check in the embedded implementation.

Finally, after later model iterations, we also visualised class means together with split planes from simplified tree models to illustrate how the classifier partitions the \((r,g,b)\) space
![ClassMeans-v2](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/images_for_doc/ClassMeans-v2.png?raw=true)
![ClassMeans-v3](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/images_for_doc/ClassMeans-v3.png?raw=true)

---

## Calibration method

### Classification approach

The classification pipeline was developed iteratively to balance **accuracy**, **robustness**, and **embedded feasibility** (integer arithmetic and compact code size). The progression was:

**Step 1 — Single decision tree using normalised RGB plus Clear (baseline).**  
The first model was a decision tree trained on \([r, g, b, C]\), where \(C\) is the clear (brightness) channel. Decision trees are interpretable and can be compiled into nested if/else comparisons. An example of the early tree structure is shown in

![DecisionTree-v1-normzalizedRGBandClear](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/images_for_doc/DecisionTree-v1-normzalizedRGBandClear.png?raw=true)


However, including \(C\) encouraged **brightness-driven splits** (distance/lighting effects) that do not generalise well between datasets, especially when mixing V1 and V2 recordings.

**Step 2 — Remove Clear from the classifier (use Clear only for normalisation).**  
To improve invariance to brightness and distance, we redesigned the feature set to use only \((r,g,b)\) and excluded \(C\) from the decision rule. The clear channel is still used to compute the ratios, and can optionally be used as a separate validity threshold (e.g., `MIN_CLEAR`) to avoid classifying extremely dark/noisy readings, but it no longer participates as a classification feature. This significantly reduced brightness-related misclassifications.

**Step 3 — Mixed dataset evaluation (V1 + V2, V1 is the collection of data with the 3D printed case. V2 is data collection in different environments with/without the case, in the following README, I will use V1 and V2 to stand for the versions).**  
We merged the two tables (`color_data` and `colordata_v2`) by selecting only the shared useful columns (clear/red/green/blue/label), computing the same normalised features, and evaluating using a stratified 75/25 train/test split. This confirmed that remaining errors were primarily caused by overlapping clusters rather than random noise.

**Step 4 — Random Forest for higher accuracy (ensemble voting).**  
A single decision tree is sensitive to threshold placement near class boundaries (e.g., *blue vs light blue*). To reduce boundary errors, we upgraded to a **Random Forest**, which combines many decision trees and outputs a majority vote. This improved stability and increased accuracy on the mixed dataset.

**Step 5 — Add discriminative features to reduce remaining overlaps.**  
To further separate the hardest pairs without reintroducing brightness sensitivity, we expanded the feature set with stable derived terms:

![sum_rgb_norm](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/images_for_doc/sum_rgb_norm.png?raw=true)

- These features improved separability for the remaining confusion pairs (especially *light blue vs blue* and *black vs green*) and produced the final high accuracy on mixed testing.

**Step 6 — Surrogate tree for embedded deployment (compact if/else).**  
Although the Random Forest achieved the best accuracy, converting hundreds of trees into C would produce very large code size. To keep the embedded implementation lightweight, we trained a **surrogate decision tree** that approximates the Random Forest behaviour while remaining a single if/else structure. This surrogate tree is suitable for integer-only C code generation. The surrogate tree is shown in ![SurrogateDecesionTreeFromRandomForest](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/images_for_doc/DecisionTree-v3-SurrogateDecesionTreeFromRandomForest.png?raw=true)

```
|--- g_norm <= 0.27949
|   |--- bg <= -0.01342
|   |   |--- r_norm <= 0.49415
|   |   |   |--- class: red
|   |   |--- r_norm >  0.49415
|   |   |   |--- sum_rgb_norm <= 1.05377
|   |   |   |   |--- rg <= 0.40738
|   |   |   |   |   |--- class: orange
|   |   |   |   |--- rg >  0.40738
|   |   |   |   |   |--- class: red
|   |   |   |--- sum_rgb_norm >  1.05377
|   |   |   |   |--- class: orange
|   |--- bg >  -0.01342
|   |   |--- g_norm <= 0.19391
|   |   |   |--- class: red
|   |   |--- g_norm >  0.19391
|   |   |   |--- class: red
|--- g_norm >  0.27949
|   |--- rg <= 0.16340
|   |   |--- r_norm <= 0.44819
|   |   |   |--- bg <= -0.08022
|   |   |   |   |--- bg <= -0.11555
|   |   |   |   |   |--- class: green
|   |   |   |   |--- bg >  -0.11555
|   |   |   |   |   |--- sum_rgb_norm <= 0.97518
|   |   |   |   |   |   |--- class: green
|   |   |   |   |   |--- sum_rgb_norm >  0.97518
|   |   |   |   |   |   |--- class: light blue
|   |   |   |--- bg >  -0.08022
|   |   |   |   |--- bg <= -0.01590
|   |   |   |   |   |--- r_norm <= 0.43810
|   |   |   |   |   |   |--- class: blue
|   |   |   |   |   |--- r_norm >  0.43810
|   |   |   |   |   |   |--- class: blue
|   |   |   |   |--- bg >  -0.01590
|   |   |   |   |   |--- class: blue
|   |   |--- r_norm >  0.44819
|   |   |   |--- b_norm <= 0.22775
|   |   |   |   |--- r_norm <= 0.45246
|   |   |   |   |   |--- sum_rgb_norm <= 0.95501
|   |   |   |   |   |   |--- class: black
|   |   |   |   |   |--- sum_rgb_norm >  0.95501
|   |   |   |   |   |   |--- class: black
|   |   |   |   |--- r_norm >  0.45246
|   |   |   |   |   |--- class: black
|   |   |   |--- b_norm >  0.22775
|   |   |   |   |--- b_norm <= 0.23067
|   |   |   |   |   |--- b_norm <= 0.23054
|   |   |   |   |   |   |--- class: white
|   |   |   |   |   |--- b_norm >  0.23054
|   |   |   |   |   |   |--- class: white
|   |   |   |   |--- b_norm >  0.23067
|   |   |   |   |   |--- class: white
|   |--- rg >  0.16340
|   |   |--- b_norm <= 0.21933
|   |   |   |--- sum_rgb_norm <= 0.98425
|   |   |   |   |--- class: yellow
|   |   |   |--- sum_rgb_norm >  0.98425
|   |   |   |   |--- class: yellow
|   |   |--- b_norm >  0.21933
|   |   |   |--- bg <= -0.07430
|   |   |   |   |--- class: pink
|   |   |   |--- bg >  -0.07430
|   |   |   |   |--- class: pink

```

### Random Forest (RF) — Per-class performance (25% test split)

| label       | total | correct | accuracy  | misclassified_as |
|------------|------:|--------:|----------:|------------------|
| blue       | 374   | 374     | 1.000000  |                  |
| green      | 375   | 375     | 1.000000  |                  |
| orange     | 375   | 375     | 1.000000  |                  |
| pink       | 375   | 375     | 1.000000  |                  |
| red        | 375   | 375     | 1.000000  |                  |
| white      | 374   | 374     | 1.000000  |                  |
| yellow     | 375   | 375     | 1.000000  |                  |
| light blue | 375   | 374     | 0.997333  | blue:1           |
| black      | 375   | 373     | 0.994667  | green:2          |

**RF overall test accuracy:** 0.9991105840498073

---

### Surrogate Tree — Per-class performance (25% test split)

| label       | total | correct | accuracy  | misclassified_as    |
|------------|------:|--------:|----------:|---------------------|
| blue       | 374   | 374     | 1.000000  |                     |
| yellow     | 375   | 375     | 1.000000  |                     |
| orange     | 375   | 374     | 0.997333  | red:1               |
| pink       | 375   | 374     | 0.997333  | blue:1              |
| red        | 375   | 374     | 0.997333  | pink:1              |
| white      | 374   | 373     | 0.997326  | blue:1              |
| light blue | 375   | 372     | 0.992000  | blue:3              |
| black      | 375   | 371     | 0.989333  | white:2, green:2    |
| green      | 375   | 370     | 0.986667  | black:5             |

**Surrogate overall test accuracy:** 0.9952564482656389  
**Surrogate agreement with RF (test):** 0.9961458642158316


Random Forest achieves a very high overall accuracy (0.9991) on the 25% held-out test split of the merged V1+V2 dataset. Most classes reach 100%, and the remaining errors are concentrated in the hardest boundary pairs: light blue → blue (1 sample) and black → green (2 samples). This indicates that the normalised feature space separates most colours well, with only small overlap between a few similar clusters.

The surrogate decision tree is a compact approximation intended for embedded deployment. Its overall accuracy is lower (0.9953) because a single tree cannot represent the full ensemble decision boundary of the forest. The per-class breakdown shows that its main weaknesses are still the same ambiguous pairs (especially green ↔ black and light blue → blue), but with more errors than the Random Forest. Despite this, the surrogate tree still matches the Random Forest’s predictions on ~99.6% of test samples (agreement = 0.9961), meaning it captures most of the ensemble behaviour while remaining a simple if/else structure suitable for conversion to integer-only C code.

---

## Mapping from colour → navigation instruction

Once a colour label is predicted, it is mapped to a navigation instruction according to the project specification. The colour recognition module outputs one of:

`black, blue, green, light blue, orange, pink, red, white, yellow`

The navigation controller converts the recognised colour into the corresponding movement command (e.g., right/left/180° turn, finish/return home). The mapping is implemented as a simple lookup (e.g., switch/case) so that navigation logic remains independent from the recognition algorithm.


# Battery Measurement
The battery level is measured at the start. If the battery level is lower than 50%, the red brake light will turn on.

There is also another TEST_MODE to measure the battery level lively through serial.

# Video Demonstrations:
## Motor Calabration

[![Watch the video](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/videos_for_doc/motor-collaboration-v1.png?raw=true)](https://github.com/shengj1ang/READMEs/raw/refs/heads/ECM-final-doc/videos_for_doc/motor-collaboration-v1.mp4)



## Colour data collection and Live time colour detecetion (debug) through serial

[![Watch the video](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/videos_for_doc/colour-reading-1.png?raw=true)](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/videos_for_doc/colour-reading-1.mp4)

## Live battery measurement through serial



## Running Demo

[![Watch the video](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/videos_for_doc/test-1.png?raw=true)](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/videos_for_doc/test-1.mp4)



[![Watch the video](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/videos_for_doc/test-2.png?raw=true)](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/videos_for_doc/test-2.mp4)

[![Watch the video](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/videos_for_doc/test-3.png?raw=true)](https://github.com/shengj1ang/READMEs/blob/ECM-final-doc/videos_for_doc/test-3.mp4)
