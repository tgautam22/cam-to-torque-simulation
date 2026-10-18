# Streamlit page for cam-to-torque. Run with:  streamlit run app.py
import streamlit as st

from calc import Params, run
from plots import animated_fig

st.set_page_config(page_title="Cam to torque", layout="wide")
st.markdown("<style>.block-container{padding-top:2rem;padding-bottom:1rem}</style>", unsafe_allow_html=True) # less empty space at the top

# ---------- inputs (sidebar) ----------
d = Params() # defaults
sb = st.sidebar
sb.title("Inputs")

sb.subheader("Cam shape")
a, b = sb.columns(2)
Rb = a.number_input("Base radius (mm)", value=d.Rb, step=1.0, min_value=0.1)
h = b.number_input("Max lift (mm)", value=d.h, step=1.0, min_value=0.0)
a, b = sb.columns(2)
rise_start = a.number_input("Rise start (°)", value=d.rise_start, step=5.0)
rise = b.number_input("Rise angle (°)", value=d.rise, step=5.0, min_value=1.0)
a, b = sb.columns(2)
dwell = a.number_input("Top dwell (°)", value=d.dwell, step=5.0, min_value=0.0)
fall = b.number_input("Fall angle (°)", value=d.fall, step=5.0, min_value=1.0)

sb.subheader("Follower and spring")
a, b = sb.columns(2)
Rf = a.number_input("Roller radius (mm)", value=d.Rf, step=0.5, min_value=0.1)
off = b.number_input("Offset d (mm)", value=d.d, step=0.5)
a, b = sb.columns(2)
k = a.number_input("Spring k (N/mm)", value=d.k, step=5.0, min_value=0.1)
s0 = b.number_input("Preload (mm)", value=d.s0, step=0.5, min_value=0.0)

travel = sb.number_input("Spring max travel (mm)", value=d.travel, step=1.0, min_value=0.1,
                         help="Free length minus solid length, from the spring's datasheet.")

p = Params(Rb=Rb, h=h, rise_start=rise_start, rise=rise, dwell=dwell, fall=fall,
           Rf=Rf, d=off, k=k, s0=s0, travel=travel)
error = p.check()


@st.cache_data # only recalculates when an input changes
def build(p):
    r = run(p)
    return r, animated_fig(r, p)


# ---------- page ----------
st.title("Cam-to-Torque Simulator")
st.caption("Set the cam shape, input the mechanical parameters, and see the lift and torque curves.")

if error:
    st.error(error)
    st.stop() # nothing below runs until the inputs are fixed

r, fig = build(p)

m1, m2, m3, m4 = st.columns(4) # one-glance summary of the whole turn
m1.metric("Max lift", f"{r.lift.max():.2f} mm")
m2.metric(f"Compression ({100 * r.s.max() / p.travel:.0f}%)", f"{r.s.max():.2f} / {p.travel:g} mm")
m3.metric("Peak torque", f"{r.T.max():.2f} N·m")
m4.metric("Lowest torque", f"{r.T.min():.2f} N·m")

tab_mech, tab_method = st.tabs(["Mechanism", "Method"])

with tab_mech:
    st.plotly_chart(fig, width="stretch", theme=None) # theme=None keeps our own fonts and colours; Play, Pause and the angle slider are inside the figure; it animates in the browser

with tab_method:
    st.caption("Every curve is calculated every 0.1°. Angles in degrees, lengths in mm, k in N/mm, torque in N·m.")
    steps = [
        ("Bump", r"L(\varphi) = h\left(x - \dfrac{\sin 2\pi x}{2\pi}\right),\quad x = \dfrac{\varphi - \varphi_{start}}{\beta_{rise}}"),
        ("Cam radius", r"R(\varphi) = R_b + L(\varphi)"),
        ("Turn the cam", r"x = R\sin(\varphi - \theta),\quad y_{point} = R\cos(\varphi - \theta)"),
        ("Roller touching a point", r"y_{roller}(\varphi) = y_{point} + \sqrt{R_f^2 - (x - d)^2}"),
        ("Roller centre", r"y_{roller}(\theta) = \max_{\varphi} y_{roller}(\varphi)"),
        ("Lift", r"\text{lift} = y_{roller} - \sqrt{(R_b + R_f)^2 - d^2}"),
        ("Compression", r"s = s_0 + \text{lift}"),
        ("Slope", r"\dfrac{ds}{d\theta} = \dfrac{s(\theta + 0.1^\circ) - s(\theta - 0.1^\circ)}{0.2^\circ \text{ in rad}}"),
        ("Torque", r"T = k\,s\,\dfrac{ds}{d\theta}"),
    ]
    for n, (label, formula) in enumerate(steps, start=1):
        left, right = st.columns([1, 3], vertical_alignment="center")
        left.markdown(f"**{n}. {label}**")
        right.latex(formula)
