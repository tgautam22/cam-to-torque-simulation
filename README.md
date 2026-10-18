# Cam to Torque Simulation

This simulations calculates the torque and lift a cam and spring-loaded roller follower produce as the cam rotates. Simulation can be used to see how various cam and follower settings impact the torque produced in a cam-spring actuator mechanism.

## Inputs

- Base radius: radius of the cam without the bump (mm)
- Max lift: height of the bump (mm)
- Rise start, rise, dwell, fall: where the bump starts and how long each part lasts (deg)
- Roller radius: radius of the roller follower (mm)
- Offset: sideways distance of the follower line from the cam centre (mm)
- Spring k: spring constant (N/mm)
- Preload: how much the spring is compressed at rest (mm)
- Spring max travel: most the spring can be compressed (mm)
- Spring angle: angle of the rod and spring from vertical (deg)

The Method tab in the app explains the calculations in detail.

## Setup

```
git clone https://github.com/tgautam22/cam-to-torque-simulation.git
cd cam-to-torque-simulation
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```
streamlit run app.py
```

## Test

```
python -m pytest
```

## Files

- calc.py: all the calculations
- plots.py: the animated mechanism and the lift and torque graphs
- app.py: the Streamlit page
- tests/test_calc.py: tests for calc.py

## References

- Realmuto, J., Klute, G., and Devasia, S. (2015). Nonlinear Passive Cam-Based Springs for Powered Ankle Prostheses. Journal of Medical Devices, 9(1), 011007.
