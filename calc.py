# Calculations for cam-to-torque: bump -> cam outline -> roller lift -> torque
# Units: mm, deg, k in N/mm, torque in N*m. Everything is calculated every 0.1 deg.
from dataclasses import dataclass

import numpy as np

STEP = 0.1 # deg


@dataclass
class Params:
    # cam shape
    Rb: float = 25.0 # base radius (mm)
    h: float = 15.0 # max lift of the bump (mm)
    rise_start: float = 0.0 # deg
    rise: float = 120.0 # deg
    dwell: float = 40.0 # deg
    fall: float = 120.0 # deg
    # follower and spring
    Rf: float = 8.0 # roller radius (mm)
    d: float = 6.0 # offset of the follower line (mm)
    k: float = 100.0 # spring constant (N/mm)
    s0: float = 5.0 # preload (mm)

    def check(self): # returns an error message, or None if the inputs are fine
        if self.Rb <= 0 or self.Rf <= 0 or self.k <= 0:
            return "Radii and k must be above zero."
        if self.h < 0 or self.s0 < 0:
            return "Max lift and preload can't be negative."
        if abs(self.d) >= self.Rb:
            return "Offset must be smaller than the base radius."
        if self.rise <= 0 or self.fall <= 0 or self.dwell < 0:
            return "Rise and fall angles must be above zero."
        if self.rise + self.dwell + self.fall > 360:
            return "Rise + dwell + fall can't be more than 360 deg."
        return None


@dataclass
class Result:
    phi: np.ndarray # cam angle of each outline point (deg)
    R: np.ndarray # cam radius at each phi (mm)
    x0: np.ndarray # outline point, sideways (mm)
    y0: np.ndarray # outline point, up (mm)
    theta: np.ndarray # cam rotation angle, 0 to 360 (deg)
    y_roller: np.ndarray # roller centre height at each theta (mm)
    lift: np.ndarray # roller lift (mm)
    s: np.ndarray # spring compression (mm)
    ds: np.ndarray # ds/dtheta (mm/rad)
    T: np.ndarray # torque (N*m)


def bump(phi, p):
    a = (np.asarray(phi, dtype=float) - p.rise_start) % 360 # angle since the rise started (wraps past 360)
    L = np.zeros_like(a) # base circle: no bump

    def cycloid(u): # smooth 0 -> 1 S-curve
        return u - np.sin(2 * np.pi * u) / (2 * np.pi)

    on_rise = a < p.rise
    on_dwell = (a >= p.rise) & (a < p.rise + p.dwell)
    on_fall = (a >= p.rise + p.dwell) & (a < p.rise + p.dwell + p.fall)

    L[on_rise] = p.h * cycloid(a[on_rise] / p.rise) # L = h*(x - sin(2*pi*x)/(2*pi))
    L[on_dwell] = p.h # L = h
    L[on_fall] = p.h * (1 - cycloid((a[on_fall] - p.rise - p.dwell) / p.fall)) # same curve reversed
    return L


def cam_outline(p):
    phi = np.arange(0, 360, STEP) # cam angles, every 0.1 deg
    R = p.Rb + bump(phi, p) # R = Rb + L(phi)
    x0 = R * np.sin(np.radians(phi)) # sideways (phi measured clockwise from the top)
    y0 = R * np.cos(np.radians(phi)) # up
    return phi, R, x0, y0


def lift_curve(phi, R, p):
    theta = np.arange(0, 360 + STEP / 2, STEP) # cam rotation angles, 0 to 360 inclusive
    y_roller = np.empty_like(theta)

    for i, th in enumerate(theta):
        a = np.radians(phi - th) # each cam point's angle from the top after turning by theta
        x = R * np.sin(a) # sideways position
        y_point = R * np.cos(a) # height
        gap = x - p.d # sideways distance from the follower line
        reach = np.abs(gap) <= p.Rf # only points the roller can touch
        y_need = y_point[reach] + np.sqrt(p.Rf**2 - gap[reach] ** 2) # roller centre if it touched each point
        y_roller[i] = y_need.max() # it sits on the highest one

    base = np.sqrt((p.Rb + p.Rf) ** 2 - p.d**2) # roller centre height on the bare base circle
    lift = y_roller - base
    return theta, y_roller, lift


def torque_curve(lift, p):
    s = p.s0 + lift # s = s0 + lift
    one_turn = s[:-1] # 0 .. 359.9 (360 repeats 0)
    ds = (np.roll(one_turn, -1) - np.roll(one_turn, 1)) / np.radians(2 * STEP) # (s(th+0.1) - s(th-0.1)) / 0.2 deg, wraps at 0/360
    ds = np.append(ds, ds[0]) # value at 360 = value at 0
    T = p.k * s * ds / 1000 # T = k*s*ds/dth, /1000 turns N*mm into N*m
    return s, ds, T


def run(p): # whole pipeline in one call
    phi, R, x0, y0 = cam_outline(p)
    theta, y_roller, lift = lift_curve(phi, R, p)
    s, ds, T = torque_curve(lift, p)
    return Result(phi, R, x0, y0, theta, y_roller, lift, s, ds, T)