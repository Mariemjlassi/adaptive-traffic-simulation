# adaptive-traffic-simulation
An adaptive traffic control simulation leveraging real-time decision logic to optimize urban flow. Includes emergency prioritization, pedestrian safety management, weather effects, and data-driven insights.

## Overview

This project models an intelligent intersection capable of reacting in real time to changing traffic conditions. The system replaces fixed signal cycles with dynamic decision logic to improve flow efficiency while maintaining pedestrian safety.

## Core Features

### Adaptive Traffic Control
The simulation continuously evaluates the state of the intersection and adjusts signal behavior accordingly:

- **Dynamic Vehicle Counting:** Monitors vehicles approaching and waiting on each axis (North–South and East–West).
- **Variable Green Duration:** Signal timing automatically adjusts between 10 and 35 seconds based on detected traffic density.
- **Predictive Switching:** When one lane is empty and another is congested, the system forces a transition to optimize throughput.

### Emergency Vehicle Management
- **Priority Detection:** Ambulances are automatically detected within a defined proximity of the intersection.
- **Immediate Right-of-Way:** The system triggers a green signal, blocks competing lanes, and extends the cycle when necessary.
- **Procedural Audio:** Realistic sirens generated using NumPy-based sound synthesis.

### Pedestrian Safety
- **On-Demand Crossing:** Pedestrian requests are registered and queued for safe signal cycles.
- **Realistic Animation:** Walking motion is computed using sinusoidal functions with multiple pedestrian profiles (children, adults, seniors).

### Dynamic Environment
- **Interactive Weather System:** Rain mode introduces visual effects, darker lighting conditions, and vehicle headlight beams.
- **Modified Driving Physics:** Rain reduces vehicle speed by 30% and increases safety distances by 20%.
- **Generated Rain Audio:** Continuous background sound produced through white-noise synthesis.

### Dashboard and Analytics
- **Real-Time Visualization:** Displays the last 12 traffic phases with load indicators.
- **Data Persistence:** Each cycle and traffic level is stored in SQLite for post-simulation analysis.

## Technical Stack

- **Language:** Python  
- **Graphics Engine:** Pygame (sprites, collisions, UI rendering)  
- **Numerical Processing:** NumPy  
- **Database:** SQLite  

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Mariemjlassi/adaptive-traffic-simulation.git
cd adaptive-traffic-simulation
pip install -r requirements.txt
python main_gui.py



