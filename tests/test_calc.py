# Tests for calc.py. Each one checks an output against something worked out separately.
import numpy as np
import pytest

from calc import STEP, Params, bump, run


def at(r, theta): # value index for a cam angle in the 0.1 deg arrays
    return int(round(theta / STEP))


def test_bump_by_hand(): # cycloid L = h*(x - sin(2*pi*x)/(2*pi)) at angles worked out on paper (h = 15, rise 0-120, dwell to 160, fall to 280)
    p = Params()
    L = bump(np.array([0, 30, 60, 140, 220, 300]), p)
    assert L[0] == pytest.approx(0) # start of the rise
    assert L[1] == pytest.approx(15 * (0.25 - 1 / (2 * np.pi))) # quarter of the rise: 1.3627 mm
    assert L[2] == pytest.approx(7.5) # half the rise: h/2
    assert L[3] == pytest.approx(15) # on the dwell: h
    assert L[4] == pytest.approx(7.5) # half the fall: h/2
    assert L[5] == pytest.approx(0) # back on the base circle


@pytest.mark.parametrize("d", [0.0, 6.0, -10.0])
def test_lift_on_base_circle_and_dwell(d): # roller on a plain circle: lift found from the triangle, no searching
    p = Params(d=d)
    r = run(p)
    on_dwell = np.sqrt((p.Rb + p.h + p.Rf) ** 2 - d**2) - np.sqrt((p.Rb + p.Rf) ** 2 - d**2) # roller on the circle of radius Rb + h
    assert r.lift[at(r, 140)] == pytest.approx(on_dwell, abs=1e-4) # 1e-4 mm: with an offset the true contact falls between two 0.1 deg outline points
    assert r.lift[at(r, 320)] == pytest.approx(0, abs=1e-4) # roller on the base circle


@pytest.mark.parametrize("d", [0.0, 6.0, -10.0])
def test_roller_sits_on_cam(d): # at any angle the roller touches the turned cam but never cuts into it
    p = Params(d=d)
    r = run(p)
    for theta in [20, 75, 140, 200, 250]:
        a = np.radians(r.phi - theta)
        x, y = r.R * np.sin(a), r.R * np.cos(a) # cam outline after turning by theta
        gap = np.hypot(x - p.d, y - r.y_roller[at(r, theta)]).min() # closest cam point to the roller centre
        assert gap >= p.Rf - 1e-9 # never inside the roller
        assert gap <= p.Rf + 0.01 # and touching it (0.01 mm allows for points every 0.1 deg)


@pytest.mark.parametrize("alpha", [0.0, 30.0, 60.0])
def test_energy_over_the_rise(alpha): # work done by the torque from base circle to dwell = energy stored in the spring
    p = Params(d=0.0, alpha=alpha)
    r = run(p)
    th = np.radians(np.arange(-40, 140 + STEP / 2, STEP)) # 320 deg (base circle) round through 0 to 140 deg (dwell)
    T = np.interp(np.degrees(th) % 360, r.theta, r.T)
    work = np.trapezoid(T, th) * 1000 # N*m*rad -> N*mm
    s_top = p.s0 + p.h * np.cos(np.radians(alpha)) # spring at the dwell, worked out by hand
    stored = 0.5 * p.k * (s_top**2 - p.s0**2) # N*mm
    assert work == pytest.approx(stored, rel=1e-3)


def test_full_turn_gives_back_its_energy(): # the cam ends where it started, so the torque adds up to zero over one turn
    r = run(Params())
    net = np.trapezoid(r.T, np.radians(r.theta))
    assert net == pytest.approx(0, abs=1e-6)


def test_no_offset_symmetric_cam(): # same rise and fall with no offset: peak torque and lowest torque are mirror images
    r = run(Params(d=0.0))
    assert r.T.max() == pytest.approx(-r.T.min(), rel=1e-6)


def test_offset_breaks_the_symmetry(): # with an offset, the push on the way up and the pull on the way down differ
    r = run(Params(d=6.0))
    assert abs(r.T.max() + r.T.min()) > 0.5


def test_spring_travel_limit(): # preload + biggest roller lift must fit in the spring's travel
    p = Params(s0=5.0, d=0.0, travel=19.0) # needs 5 + 15 = 20 mm
    assert p.check() is not None and "travel" in p.check()
    assert Params(s0=5.0, d=0.0, travel=20.5).check() is None
    assert Params(s0=5.0, d=0.0, alpha=60.0, travel=13.0).check() is None # at 60 deg it only needs 5 + 15*cos60 = 12.5 mm


def test_bad_inputs():
    assert Params(alpha=90.0).check() is not None
    assert Params(d=25.0).check() is not None # offset as big as the base radius
    assert Params(rise=200, dwell=40, fall=200).check() is not None # bump longer than one turn
    assert Params().check() is None